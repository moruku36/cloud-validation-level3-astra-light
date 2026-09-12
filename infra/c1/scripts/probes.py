"""Bounded future probes; imported only after c1.guard. No cloud calls on import."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid
from c1 import (ApiError, Stop, Aws, atomic, bucket_args, caller_policy, classify_denial,
                classify_lock, expected_account, private_path, resolved_operator_role_arn,
                now, digest, REGION, LIMITS, timestamp)

def put(api, bucket, key, path, conditional=False):
    if Path(path).stat().st_size > 1_048_576:
        raise Stop("Payload exceeds 1MiB")
    args = bucket_args(api.c, bucket) + ["--key", key, "--body", str(path),
            "--server-side-encryption", "aws:kms", "--ssekms-key-id", api.c["kms_arn"]]
    if conditional:
        args += ["--if-none-match", "*"]
    return api.call("s3api", "put-object", args)

def iam_probe(api, c, approval):
    # Destructive denial uses a disposable canary, NEVER the actual State object.
    if not approval.get("canary_substitution_approved"):
        raise Stop("Review canary substitution before IAM probe")
    operator = Aws(c, c["aws_profile"])
    operator.identity(caller_policy(c))
    directory = private_path(c["evidence_dir"])
    sample = directory / "canary.private.txt"
    sample.write_text("CP1 synthetic canary\n", encoding="utf-8")
    denied_key = "denied/canary"
    seeded = put(operator, c["backend_bucket"], denied_key, sample)
    if not seeded.get("VersionId"):
        raise Stop("Versioned canary seed unconfirmed")
    allowed_key = "synthetic/canary"
    put(api, c["fixture_bucket"], allowed_key, sample)
    output = directory / "canary-read.private.txt"
    api.call("s3api", "get-object", bucket_args(c, c["fixture_bucket"]) +
             ["--key", allowed_key, str(output)])
    if digest(output) != digest(sample):
        raise Stop("Allowed control failed")
    results = {}
    for op in ("get-object", "delete-object"):
        args = bucket_args(c, c["backend_bucket"]) + ["--key", denied_key]
        if op == "get-object":
            args += [str(directory / "unexpected.private.txt")]
        try:
            api.call("s3api", op, args)
            result = classify_denial("SUCCESS")
        except ApiError as exc:
            result = classify_denial(exc.code)
        results[op] = result
        if result != "EXPECTED_DENY":
            atomic(directory / "iam-probe.private.json", {"results": results, "status": "STOP"})
            raise Stop("IAM probe failed or unknown; inspect canary and stop")
    return {"results": results, "allowed_control": "PASS", "actual_state_delete_tested": False,
            "canary_seed_version": seeded["VersionId"], "at": now().isoformat()}

def reserve_terraform(api, reservation):
    if api.c.get("_new_work_deadline") and (timestamp(api.c["_new_work_deadline"]) - now()).total_seconds() < 180:
        raise Stop("Insufficient time before new-work deadline")
    # Terraform's internal calls are not observable by this wrapper. Reserve a reviewed bound.
    # If that bound cannot be justified at the real Plan gate, execution stays blocked.
    mutex = api.dir / "request.guard"
    try:
        fd = os.open(mutex, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise Stop("Concurrent ledger access") from exc
    try:
        os.close(fd)
        data = json.loads(api.ledger.read_text()) if api.ledger.exists() else {k: 0 for k in LIMITS}
        for k, limit in LIMITS.items():
            n = reservation.get(k)
            if not isinstance(n, int) or n <= 0 or data[k] + n > limit * 0.8:
                raise Stop("Missing/invalid Terraform request bound")
            data[k] += n
        atomic(api.ledger, data)
    finally:
        mutex.unlink(missing_ok=True)

def lock_probe(api, c, approval, runner=subprocess.run):
    if not approval.get("all_writers_stopped") or not approval.get("terraform_bound_reviewed"):
        raise Stop("Idle owner and Terraform request-bound review required")
    workdir = private_path(c["fixture_workdir"])
    tfvars = private_path(c["fixture_tfvars"])
    source = Path(__file__).resolve().parents[1] / "fixture"
    files = lambda d: {p.name: digest(p) for p in d.iterdir()
                       if p.suffix == ".tf" or p.name.endswith(".tf.json") or p.name == ".terraform.lock.hcl"}
    if files(workdir) != files(source):
        raise Stop("Fixture working copy changed")
    backend = json.loads((workdir / ".terraform" / "terraform.tfstate").read_text()).get("backend", {})
    if backend.get("type") != "s3" or any(backend.get("config", {}).get(k) != v for k,v in {
            "bucket":c["backend_bucket"],"key":c["state_key"],"region":REGION,
            "kms_key_id":c["kms_arn"],"use_lockfile":True}.items()):
        raise Stop("Probe backend scope mismatch")
    values = json.loads(tfvars.read_text())
    expected = {"account_id": expected_account(c), "experiment_id": c["experiment_id"],
                "operator_arn": resolved_operator_role_arn(c), "expires_at": c["expires_at"],
                "kms_arn": c["kms_arn"]}
    if any(values.get(k) != v for k, v in expected.items()):
        raise Stop("Probe input scope mismatch")
    if approval.get("fixture_tfvars_sha256") != digest(tfvars):
        raise Stop("Input version changed")
    executable = Path(c["terraform_executable"]).resolve()
    if digest(executable) != approval.get("terraform_binary_sha256"):
        raise Stop("Terraform executable mismatch")
    directory = private_path(c["evidence_dir"])
    lock_id = str(uuid.uuid4())
    lock_key = c["state_key"] + ".tflock"
    payload = directory / "owned-lock.private.json"
    atomic(payload, {"ID": lock_id, "Operation": "OperationTypePlan", "Info": "CP1 conditional lock probe",
                     "Who": "CP1-synthetic", "Version": "1.13.5", "Created": now().isoformat(),
                     "Path": c["backend_bucket"] + "/" + c["state_key"]})
    reserve_terraform(api, approval.get("terraform_request_reservation", {}))
    put(api, c["backend_bucket"], lock_key, payload, conditional=True)
    # On timeout/unknown ownership preserve the lock and request operator inspection.
    env = {k:v for k,v in os.environ.items() if not k.startswith(("AWS_", "TF_"))}
    cli_config = directory / "probe.tfrc"
    cli_config.write_text("disable_checkpoint = true\n", encoding="utf-8")
    env.update(AWS_PROFILE=c["profiles"]["apply"], AWS_REGION=REGION,
               AWS_EC2_METADATA_DISABLED="true", AWS_IGNORE_CONFIGURED_ENDPOINT_URLS="true",
               AWS_MAX_ATTEMPTS="1", CHECKPOINT_DISABLE="1", TF_IN_AUTOMATION="1",
               TF_WORKSPACE="default", TF_CLI_CONFIG_FILE=str(cli_config))
    p = runner([str(executable), "-chdir=" + str(workdir), "plan", "-input=false",
                "-no-color", "-lock-timeout=0s", "-refresh=false", "-var-file=" + str(tfvars)],
               capture_output=True, text=True, env=env, timeout=60)
    result = classify_lock(p.returncode, p.stderr + p.stdout, lock_id)
    if result != "EXPECTED_LOCK_CONFLICT":
        atomic(directory / "lock-probe.private.json", {"status": result, "lock_id": lock_id,
                                                     "manual_inspection_required": True})
        raise Stop("Lock result unexpected; preserve lock until owner inspected")
    readback = directory / "read-lock.private.json"
    api.call("s3api", "get-object", bucket_args(c, c["backend_bucket"]) +
             ["--key", lock_key, str(readback)])
    if json.loads(readback.read_text()).get("ID") != lock_id:
        raise Stop("Lock ownership changed; never force-unlock")
    api.call("s3api", "delete-object", bucket_args(c, c["backend_bucket"]) + ["--key", lock_key])
    # A second approved Plan should succeed once the conditional lock is released.
    reserve_terraform(api, approval.get("terraform_request_reservation", {}))
    control = runner([str(executable), "-chdir=" + str(workdir), "plan", "-input=false",
                      "-no-color", "-lock-timeout=0s", "-refresh=false", "-var-file=" + str(tfvars)],
                     capture_output=True, text=True, env=env, timeout=60)
    if control.returncode != 0:
        raise Stop("Unlocked positive control failed/unknown")
    return {"status": result, "unlocked_control": "PASS", "actual_apply_tested": False,
            "method": "conditional S3 holder versus Terraform native lock",
            "at": now().isoformat()}
