"""Future guarded Terraform steps. Does not run on import or in local unit tests."""
import json
import os
from pathlib import Path
import subprocess
from c1 import (Stop, REGION, private_path, digest, atomic, check_plan, expected_account,
                resolved_operator_role_arn)
from probes import reserve_terraform

def terraform_step(api, c, a, action, runner=subprocess.run):
    stack, step = action.split("-")
    workdir = private_path(c[stack + "_workdir"])
    tfvars = private_path(c[stack + "_tfvars"])
    executable = Path(c["terraform_executable"]).resolve()
    if digest(executable) != a.get("terraform_binary_sha256"):
        raise Stop("Unapproved Terraform executable")
    if digest(tfvars) != a.get(stack + "_tfvars_sha256"):
        raise Stop("Input file changed")
    values = json.loads(tfvars.read_text())
    expected = {"account_id": expected_account(c), "experiment_id": c["experiment_id"],
                "operator_arn": resolved_operator_role_arn(c), "expires_at": c["expires_at"]}
    for key, value in expected.items():
        if values.get(key) != value:
            raise Stop("Terraform inputs differ from approved configuration")
    if values.get("execution_authorized") is not True:
        raise Stop("Execution remains disabled in tfvars")
    if stack == "fixture" and values.get("kms_arn") != c.get("kms_arn"):
        raise Stop("Fixture key differs from binding")
    source = Path(__file__).resolve().parents[1] / stack
    expected = {p.name:digest(p) for p in source.iterdir() if p.suffix == ".tf" or p.name == ".terraform.lock.hcl"}
    actual = {p.name:digest(p) for p in workdir.iterdir()
              if p.suffix == ".tf" or p.name.endswith(".tf.json") or p.name == ".terraform.lock.hcl"}
    if actual != expected:
        raise Stop("Working copy code/lock differs from approved source")
    if stack == "fixture" and step != "init":
        meta = workdir / ".terraform" / "terraform.tfstate"
        if not meta.exists():
            raise Stop("Remote backend not initialized under approved binding")
        backend = json.loads(meta.read_text()).get("backend", {})
        config = backend.get("config", {})
        if backend.get("type") != "s3" or any(config.get(k) != v for k,v in {
                "bucket":c["backend_bucket"],"key":c["state_key"],"region":REGION,
                "kms_key_id":c["kms_arn"],"use_lockfile":True}.items()):
            raise Stop("Cached backend differs from approved scope")
    if not a.get("terraform_bound_reviewed"):
        raise Stop("Terraform request bound not reviewed")
    reserve_terraform(api, a.get("terraform_request_reservation", {}))
    profile = c["aws_profile"] if stack == "bootstrap" else c["profiles"]["apply"]
    env = {k:v for k,v in os.environ.items() if not k.startswith(("AWS_", "TF_"))}
    cli_config = private_path(c["evidence_dir"]) / "execution.tfrc"
    cli_config.write_text("disable_checkpoint = true\n", encoding="utf-8")
    env.update(AWS_PROFILE=profile, AWS_REGION=REGION, AWS_MAX_ATTEMPTS="1",
               AWS_EC2_METADATA_DISABLED="true", AWS_IGNORE_CONFIGURED_ENDPOINT_URLS="true",
               AWS_STS_REGIONAL_ENDPOINTS="regional", TF_IN_AUTOMATION="1", TF_WORKSPACE="default",
               TF_CLI_CONFIG_FILE=str(cli_config), CHECKPOINT_DISABLE="1")
    plan = workdir / "reviewed.tfplan"
    args = [str(executable), "-chdir=" + str(workdir)]
    if step == "init" and stack == "bootstrap":
        if (workdir / "terraform.tfstate").exists():
            raise Stop("Bootstrap State exists; review recovery rather than starting a new run")
        args += ["init", "-input=false", "-lockfile=readonly"]
    elif step == "init":
        backend = private_path(c["backend_config"])
        if digest(backend) != a.get("backend_config_sha256"):
            raise Stop("Backend config not approved")
        configured = json.loads(backend.read_text())
        wanted = dict(bucket=c["backend_bucket"],key=c["state_key"],region=REGION,encrypt=True,
                       kms_key_id=c["kms_arn"],use_lockfile=True,allowed_account_ids=[expected_account(c)],max_retries=1)
        if configured != wanted:
            raise Stop("Unexpected backend configuration")
        # First binding only. Never force-copy or silently overwrite an existing remote State.
        if (workdir / "terraform.tfstate").exists() or (workdir / ".terraform" / "terraform.tfstate").exists():
            raise Stop("Existing State/backend: separately review migration; no force-copy")
        args += ["init", "-input=false", "-lockfile=readonly", "-backend-config=" + str(backend)]
    elif step == "plan":
        preflight = private_path(c["evidence_dir"]) / "preflight.private.json"
        if not preflight.exists() or digest(preflight) != a.get("preflight_receipt_sha256"):
            raise Stop("Preflight not bound")
        args += ["plan", "-input=false", "-no-color", "-lock-timeout=0s",
                 "-parallelism=1", "-var-file=" + str(tfvars), "-out=" + str(plan)]
    else:
        if not plan.exists() or digest(plan) != a.get(stack + "_plan_sha256"):
            raise Stop("The exact saved Plan has not been human approved")
        if not a.get(stack + "_plan_approved"):
            raise Stop("Plan approval missing")
        args += ["apply", "-input=false", "-no-color", "-parallelism=1", str(plan)]
    try:
        result = runner(args, capture_output=True, text=True, env=env, timeout=180)
    except subprocess.TimeoutExpired as exc:
        raise Stop("Terraform timed out; stop, inspect partial resources/State/lock") from exc
    if result.returncode != 0:
        # Raw output can contain State/account details; retain only on the approved private disk.
        atomic(private_path(c["evidence_dir"]) / (action + "-failure.private.json"),
               {"stdout":result.stdout,"stderr":result.stderr,"status":"UNKNOWN_PARTIAL"})
        raise Stop("Terraform failed; inspect private result; do not rerun blindly")
    if step == "plan":
        shown = runner([str(executable), "-chdir=" + str(workdir), "show", "-json", str(plan)],
                       capture_output=True, text=True, env=env, timeout=60)
        if shown.returncode:
            raise Stop("Could not inspect Plan")
        parsed = json.loads(shown.stdout)
        review = check_plan(parsed, stack)
        atomic(workdir / "reviewed.plan.private.json", parsed)
        return {"plan_sha256":digest(plan), "review":review, "apply_approved":False}
    return {"step":action,"command_completed":True,"cloud_behaviour_requires_evidence":True}
