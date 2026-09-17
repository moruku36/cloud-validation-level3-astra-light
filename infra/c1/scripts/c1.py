"""CP1 future-operation guard. Default CLI is offline; no credential discovery on import."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

REGION = "ap-northeast-1"
REPO = Path(__file__).resolve().parents[3]
JST = dt.timezone(dt.timedelta(hours=9))
BLOCKED_ACCOUNTS = {str(n) * 12 for n in range(10)} | {"123456789012"}
CLEANUP = {"cleanup-fixture", "cleanup-backend", "schedule-key", "cleanup-roles", "residual"}
ACTIONS = {"preflight", "bind", "iam-probe", "lock-probe",
           "bootstrap-init", "bootstrap-plan", "bootstrap-apply", "fixture-init", "fixture-plan", "fixture-apply"} | CLEANUP
REQUIRED_APPROVALS = ("environment", "operators", "schedule", "budget", "metadata_exception",
                      "failed_design_exception", "key_residual_exception", "phased_budget")
LIMITS = {"tier1": 1000, "tier2": 2000, "kms": 10000, "egress": 1_000_000_000}
BOOT_TYPES = {
    "aws_kms_key.state", "aws_s3_bucket.state", "aws_s3_bucket_versioning.state",
    "aws_s3_bucket_public_access_block.state", "aws_s3_bucket_ownership_controls.state",
    "aws_s3_bucket_server_side_encryption_configuration.state", "aws_s3_bucket_policy.state",
    *{f'aws_iam_role.experiment["{r}"]' for r in ("plan", "apply", "cleanup")},
    *{f'aws_iam_role_policy.experiment["{r}"]' for r in ("plan", "apply", "cleanup")},
}
FIX_TYPES = {f"{t}.fixture" for t in (
    "aws_s3_bucket", "aws_s3_bucket_versioning", "aws_s3_bucket_public_access_block",
    "aws_s3_bucket_ownership_controls", "aws_s3_bucket_server_side_encryption_configuration",
    "aws_s3_bucket_policy")}

class Stop(RuntimeError):
    pass

class ApiError(Stop):
    def __init__(self, code):
        super().__init__(code)
        self.code = code

def now():
    return dt.datetime.now(dt.timezone.utc)

def timestamp(value):
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError()
        return result
    except (TypeError, ValueError, AttributeError) as exc:
        raise Stop("Explicit timezone timestamp required") from exc

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def code_digest():
    root = Path(__file__).resolve().parents[1]
    files = sorted(p for p in root.rglob("*") if p.is_file()
                   and ".terraform" not in p.parts
                   and (p.suffix in {".py", ".tf"} or p.name == ".terraform.lock.hcl"))
    return hashlib.sha256("".join(p.relative_to(root).as_posix() + ":" + digest(p)
                                 for p in files).encode()).hexdigest()

def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, path)

def private_path(path):
    result = Path(path).resolve()
    if result == REPO or REPO in result.parents:
        raise Stop("Private inputs/evidence must be outside the repository")
    return result

def validate_config(c):
    if not re.fullmatch(r"[0-9]{12}", c.get("account_id", "")) or c["account_id"] in BLOCKED_ACCOUNTS:
        raise Stop("Real confirmed account required; dummy account rejected")
    if c.get("region") != REGION or not re.fullmatch(r"c1-[0-9a-f]{16}", c.get("experiment_id", "")):
        raise Stop("Region/experiment mismatch")
    base = c["experiment_id"] + "-" + c["account_id"]
    if c.get("backend_bucket") != base + "-state" or c.get("fixture_bucket") != base + "-fixture":
        raise Stop("Bucket names outside exact scope")
    if c.get("state_key") != "state/" + c["experiment_id"] + "/terraform.tfstate":
        raise Stop("State path mismatch")
    if not re.fullmatch(r"arn:aws:iam::" + c["account_id"] + r":role/[A-Za-z0-9_+=,.@/-]+", c.get("operator_arn", "")):
        raise Stop("Existing same-account operator role required")
    expected = {r: f'arn:aws:iam::{c["account_id"]}:role/{base}-{r}' for r in ("plan", "apply", "cleanup")}
    if c.get("roles") != expected:
        raise Stop("Role scope mismatch")
    private_path(c.get("evidence_dir", ""))
    return c

def guard(c, approval, action, live, at=None):
    validate_config(c)
    if not live or action not in ACTIONS:
        raise Stop("Live action requires explicit --live; no AWS call was made")
    if approval.get("config_sha256") != hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest():
        raise Stop("Approval is not bound to this configuration")
    if approval.get("code_sha256") != code_digest():
        raise Stop("Implementation changed after approval")
    if approval.get("status") != "HUMAN_APPROVED":
        raise Stop("Human approval record required")
    if not all(approval.get(k) is True for k in REQUIRED_APPROVALS):
        raise Stop("Human approval fields incomplete")
    if action not in approval.get("actions", []):
        raise Stop("This action is not approved")
    if c.get("unpriced_incremental_costs") != []:
        raise Stop("Unbounded U blocks live operation")
    if c.get("budget_jpy") != 500 or not c.get("domestic_encrypted_workspace_confirmed"):
        raise Stop("Budget/workspace binding missing")
    start, end = timestamp(approval["start"]), timestamp(approval["end"])
    if timestamp(c.get("expires_at")) != end:
        raise Stop("Resource expiry tags must match the approved end")
    if end <= start or end - start > dt.timedelta(hours=6):
        raise Stop("Maximum six hours")
    if start.astimezone(JST).date() != end.astimezone(JST).date():
        raise Stop("No overnight active resources")
    at = at or now()
    if action == "residual":
        if not approval.get("separate_residual_approval"):
            raise Stop("Later read-only closeout requires separate approval")
    elif at < start:
        raise Stop("Before approved window")
    elif action not in CLEANUP and (at >= end - dt.timedelta(hours=1) or at >= start + dt.timedelta(hours=5)):
        raise Stop("New work stopped for cleanup")
    # Expiry never destroys the ability to clean up the already approved exact resources.
    if action not in CLEANUP:
        estimate = c.get("estimated_total_jpy")
        if not isinstance(estimate, (int, float)) or isinstance(estimate, bool) or not math.isfinite(estimate) or not 0 <= estimate < 300:
            raise Stop("Cost stop reached or estimate absent")
    if action not in CLEANUP:
        observed = timestamp(approval.get("cost_observed_at"))
        if observed > at or at - observed > dt.timedelta(minutes=15):
            raise Stop("Refresh cost/quantity assessment at least every 15 minutes")

def classify_denial(code):
    if code == "SUCCESS":
        return "FAIL_UNEXPECTED_ALLOW"
    if code in {"AccessDenied", "AccessDeniedException"}:
        return "EXPECTED_DENY"
    return "UNKNOWN"

def classify_lock(returncode, stderr, lock_id):
    if returncode == 0:
        return "FAIL_UNEXPECTED_LOCK_BYPASS"
    if "Error acquiring the state lock" in stderr and lock_id in stderr and (
            "PreconditionFailed" in stderr or "StatusCode: 412" in stderr):
        return "EXPECTED_LOCK_CONFLICT"
    return "UNKNOWN"

def classify_residual(code, state=None):
    if code == "NotFoundException":
        return "ABSENT"
    if code != "SUCCESS":
        return "UNKNOWN"
    return "RESIDUAL_PENDING" if state == "PendingDeletion" else "FAIL_UNEXPECTED_KEY_STATE"

def check_plan(plan, stack, mode="create"):
    """Offline allowlist triage, not a replacement for human review of the complete Plan."""
    if stack not in {"bootstrap", "fixture"} or mode not in {"create", "destroy"}:
        raise Stop("Unknown stack/mode")
    if stack == "bootstrap" and mode == "destroy":
        raise Stop("Bootstrap destruction is only through the reviewed cleanup runbook")
    allowed = BOOT_TYPES if stack == "bootstrap" else FIX_TYPES
    changes = []
    for change in plan.get("resource_changes", []):
        if change.get("mode") != "managed":
            raise Stop("Unreviewed data source")
        addr = change["address"]
        acts = change["change"]["actions"]
        expected_action = "delete" if mode == "destroy" else "create"
        if addr not in allowed or acts not in (["no-op"], [expected_action]):
            raise Stop("Out-of-scope address/update/replacement/import")
        if change["change"].get("importing"):
            raise Stop("Import of existing resources forbidden")
        if acts != ["no-op"]:
            changes.append(addr)
    if not changes:
        raise Stop("No proposed change")
    return {"stack": stack, "mode": mode, "addresses": sorted(changes), "human_review_required": True}

class Aws:
    def __init__(self, c, profile, runner=subprocess.run):
        self.c, self.profile, self.runner = c, profile, runner
        self.dir = private_path(c["evidence_dir"])
        self.dir.mkdir(parents=True, exist_ok=True)
        self.ledger = self.dir / "usage.private.json"

    def call(self, service, operation, args=(), *, cleanup=False):
        if not cleanup and self.c.get("_new_work_deadline") and now() >= timestamp(self.c["_new_work_deadline"]):
            raise Stop("New-work deadline reached")
        # Serialized reservation survives failed requests. No retries; CLI configured to one attempt.
        mutex = self.dir / "request.guard"
        try:
            fd = os.open(mutex, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise Stop("Concurrent request or interrupted ledger; inspect before recovery") from exc
        try:
            os.close(fd)
            data = json.loads(self.ledger.read_text()) if self.ledger.exists() else {k: 0 for k in LIMITS}
            # Deliberately overcharge local budget accounting; S3 operations include possible KMS calls.
            delta = {"tier1": 1, "tier2": 1, "kms": 2, "egress": 1_048_576}
            for k in LIMITS:
                if data[k] + delta[k] > LIMITS[k] * (1 if cleanup else 0.8):
                    raise Stop("Quantity envelope exhausted; do not silently raise it")
                data[k] += delta[k]
            atomic(self.ledger, data)
        finally:
            mutex.unlink(missing_ok=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith("AWS_")}
        env.update(AWS_EC2_METADATA_DISABLED="true", AWS_MAX_ATTEMPTS="1",
                   AWS_IGNORE_CONFIGURED_ENDPOINT_URLS="true", AWS_STS_REGIONAL_ENDPOINTS="regional",
                   AWS_PAGER="", AWS_CLI_AUTO_PROMPT="off")
        command = ["aws", "--profile", self.profile, "--region", REGION, "--output", "json",
                   "--no-cli-pager", "--cli-connect-timeout", "10", "--cli-read-timeout", "30",
                   service, operation, *args]
        try:
            p = self.runner(command, capture_output=True, text=True, env=env, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ApiError("TRANSPORT_UNKNOWN") from exc
        if p.returncode:
            match = re.search(r"An error occurred \(([^)]+)\)", p.stderr)
            raise ApiError(match.group(1) if match else "CLI_UNKNOWN")
        if len(p.stdout.encode()) > 1_048_576:
            raise Stop("Response larger than per-call reservation; stop and reconcile usage")
        return json.loads(p.stdout or "{}")

    def identity(self, expected_role):
        result = self.call("sts", "get-caller-identity", cleanup=True)
        expected_name = expected_role.split(":role/")[-1].split("/")[-1]
        if result.get("Account") != self.c["account_id"] or not re.fullmatch(
            rf'arn:aws:sts::{self.c["account_id"]}:assumed-role/{re.escape(expected_name)}/[^/]+',
            result.get("Arn", "")
        ):
            raise Stop("Caller account/role mismatch")

def bucket_args(c, bucket):
    if bucket not in {c["backend_bucket"], c["fixture_bucket"]}:
        raise Stop("Bucket outside manifest")
    return ["--bucket", bucket, "--expected-bucket-owner", c["account_id"]]

def bucket_owned(api, bucket):
    c = api.c
    region = api.call("s3api", "get-bucket-location", bucket_args(c, bucket), cleanup=True)
    if region.get("LocationConstraint") != REGION:
        raise Stop("Bucket region mismatch")
    tags = api.call("s3api", "get-bucket-tagging", bucket_args(c, bucket), cleanup=True)
    if {v["Key"]: v["Value"] for v in tags["TagSet"]}.get("Experiment") != c["experiment_id"]:
        raise Stop("Tag mismatch; tag alone is never sufficient")

def key_owned(api):
    c = api.c
    arn = c.get("kms_arn", "")
    if not re.fullmatch(r"arn:aws:kms:" + REGION + ":" + c["account_id"] + r":key/[0-9a-f-]{36}", arn):
        raise Stop("Actual bootstrap key binding required")
    info = api.call("kms", "describe-key", ["--key-id", arn], cleanup=True)["KeyMetadata"]
    if info.get("Arn") != arn or info.get("MultiRegion") or info.get("KeySpec") != "SYMMETRIC_DEFAULT":
        raise Stop("Key scope mismatch")
    tags = api.call("kms", "list-resource-tags", ["--key-id", arn], cleanup=True)
    if {v["TagKey"]: v["TagValue"] for v in tags["Tags"]}.get("Experiment") != c["experiment_id"]:
        raise Stop("Key tag mismatch")
    return info

def versions(api, bucket):
    rows, key_marker, version_marker = [], None, None
    while True:
        args = bucket_args(api.c, bucket) + ["--max-keys", "100", "--no-paginate"]
        if key_marker:
            args += ["--key-marker", key_marker]
        if version_marker:
            args += ["--version-id-marker", version_marker]
        page = api.call("s3api", "list-object-versions", args, cleanup=True)
        rows += page.get("Versions", []) + page.get("DeleteMarkers", [])
        if len(rows) > 60 or sum(r.get("Size", 0) for r in rows) > 60 * 1_048_576:
            raise Stop("Cleanup volume outside reviewed small fixture; human intervention")
        if not page.get("IsTruncated"):
            return rows
        key_marker, version_marker = page.get("NextKeyMarker"), page.get("NextVersionIdMarker")
        if not key_marker:
            raise Stop("Malformed pagination")

def absent_bucket(api, bucket):
    try:
        api.call("s3api", "get-bucket-location", bucket_args(api.c, bucket), cleanup=True)
    except ApiError as exc:
        if exc.code == "NoSuchBucket":
            return True
        raise Stop("Absence unconfirmed") from exc
    return False

def purge(api, bucket, binding):
    if bucket not in binding["created_buckets"]:
        raise Stop("No reviewed creation receipt")
    bucket_owned(api, bucket)
    uploads = api.call("s3api", "list-multipart-uploads",
                      bucket_args(api.c, bucket) + ["--max-uploads", "1", "--no-paginate"], cleanup=True)
    if uploads.get("Uploads") or uploads.get("IsTruncated"):
        raise Stop("Unexpected multipart upload; do not erase unknown content")
    rows = versions(api, bucket)
    # Writers must be stopped by the operator before approval of this inventory hash.
    inventory_hash = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    if binding.get("purge_inventory_sha256", {}).get(bucket) != inventory_hash:
        atomic(api.dir / (bucket + ".inventory.private.json"), rows)
        raise Stop("Review current all-version inventory hash before purge")
    for row in rows:
        api.call("s3api", "delete-object", bucket_args(api.c, bucket) +
                 ["--key", row["Key"], "--version-id", row["VersionId"]], cleanup=True)
    if versions(api, bucket):
        raise Stop("Versions remain or writer recreated data")
    api.call("s3api", "delete-bucket", bucket_args(api.c, bucket), cleanup=True)
    if not absent_bucket(api, bucket):
        raise Stop("Bucket still present")
    return {"bucket": bucket, "status": "ABSENT", "at": now().isoformat()}

def run_action(c, a, action):
    c = dict(c)
    c["_new_work_deadline"] = min(timestamp(a["end"]) - dt.timedelta(hours=1),
                                  timestamp(a["start"]) + dt.timedelta(hours=5)).isoformat()
    profiles = c["profiles"]
    kind = "apply" if action in {"iam-probe", "lock-probe", "fixture-init", "fixture-plan", "fixture-apply"} else "cleanup"
    if action in {"preflight", "bind", "cleanup-roles", "residual", "bootstrap-init", "bootstrap-plan", "bootstrap-apply"}:
        kind = "operator"
    api = Aws(c, profiles[kind])
    api.identity(c["operator_arn"] if kind == "operator" else c["roles"][kind])
    evidence = private_path(c["evidence_dir"])
    receipt_path = evidence / "creation.private.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    if action in {"iam-probe", "lock-probe", "fixture-plan", "fixture-apply"} and receipt:
        observer = Aws(c, profiles["operator"])
        observer.identity(c["operator_arn"])
        for bucket in receipt.get("created_buckets", []):
            if not absent_bucket(observer, bucket):
                rows = versions(observer, bucket)
                if len(rows) >= 45 or sum(r.get("Size", 0) for r in rows) >= 45 * 1_048_576:
                    raise Stop("Stop new work before the 60-version cleanup ceiling")
    if action in {"bootstrap-init", "bootstrap-plan", "bootstrap-apply", "fixture-init", "fixture-plan", "fixture-apply"}:
        from tf_steps import terraform_step
        result = terraform_step(api, c, a, action)
    elif action == "preflight":
        for bucket in [c["backend_bucket"], c["fixture_bucket"]]:
            if not absent_bucket(api, bucket):
                raise Stop("Name already exists; no adoption/import")
        for arn in c["roles"].values():
            try:
                api.call("iam", "get-role", ["--role-name", arn.split("/")[-1]])
            except ApiError as exc:
                if exc.code == "NoSuchEntity":
                    continue
                raise
            raise Stop("Role already exists")
        result = {"absent_before_creation": True, "config_hash": a["config_sha256"],
                  "at": now().isoformat()}
    elif action == "bind":
        # Human reviewed bootstrap output/State lineage and creation receipts, not tag-only discovery.
        if not a.get("creation_receipts_reviewed") or not a.get("preflight_receipt_sha256"):
            raise Stop("Creation provenance not approved")
        preflight = evidence / "preflight.private.json"
        if not preflight.exists() or digest(preflight) != a["preflight_receipt_sha256"]:
            raise Stop("Preflight receipt mismatch")
        created = []
        for b in [c["backend_bucket"], c["fixture_bucket"]]:
            if not absent_bucket(api, b):
                bucket_owned(api, b)
                created.append(b)
        if c["backend_bucket"] not in created:
            raise Stop("Backend creation not confirmed")
        key_owned(api)
        role_ids = {}
        for arn in c["roles"].values():
            role = api.call("iam", "get-role", ["--role-name", arn.split("/")[-1]])["Role"]
            if role["Arn"] != arn:
                raise Stop("Role binding mismatch")
            role_ids[arn] = role["RoleId"]
        result = {"created_buckets": created, "role_ids": role_ids,
                  "key_arn": c["kms_arn"], "experiment_id": c["experiment_id"],
                  "creation_plan_sha256": a["creation_plan_sha256"]}
        atomic(receipt_path, result)
    elif action.startswith("cleanup-") or action == "schedule-key":
        if not a.get("all_writers_stopped"):
            raise Stop("All writers must be stopped before cleanup")
        if receipt.get("experiment_id") != c["experiment_id"] or receipt.get("key_arn") != c["kms_arn"]:
            raise Stop("Creation receipt does not match")
        receipt["purge_inventory_sha256"] = a.get("purge_inventory_sha256", {})
        if action == "cleanup-fixture":
            result = purge(api, c["fixture_bucket"], receipt)
        elif action == "cleanup-backend":
            if not absent_bucket(api, c["fixture_bucket"]) or not a.get("state_export_verified") or not a.get("all_writers_stopped"):
                raise Stop("Fixture absence and private recovery export/writer stop required")
            result = purge(api, c["backend_bucket"], receipt)
        elif action == "schedule-key":
            for b in receipt["created_buckets"]:
                if not absent_bucket(api, b):
                    raise Stop("Encrypted dependency remains")
            info = key_owned(api)
            if not a.get("local_state_dependencies_cleared"):
                raise Stop("Preserve key while local encrypted dependency remains")
            if info.get("KeyState") == "PendingDeletion":
                result = {"KeyId": c["kms_arn"], "KeyState": "PendingDeletion",
                          "DeletionDate": info.get("DeletionDate")}
            else:
                result = api.call("kms", "schedule-key-deletion", ["--key-id", c["kms_arn"],
                             "--pending-window-in-days", "7"], cleanup=True)
            if result.get("KeyState") != "PendingDeletion" or not result.get("DeletionDate"):
                raise Stop("Deletion scheduling unconfirmed")
            result.update(status="RESIDUAL_PENDING", region=REGION, key_arn=c["kms_arn"],
                          later_owner_ref=a["later_owner_ref"], at=now().isoformat())
        else:
            pending = evidence / "schedule-key.private.json"
            if not pending.exists() or json.loads(pending.read_text()).get("status") != "RESIDUAL_PENDING":
                raise Stop("Preserve cleanup role until key receipt is safe")
            for arn in c["roles"].values():
                name = arn.split("/")[-1]
                try:
                    role = api.call("iam", "get-role", ["--role-name", name], cleanup=True)["Role"]
                except ApiError as exc:
                    if exc.code == "NoSuchEntity" and arn in receipt["role_ids"]:
                        continue
                    raise
                if role["Arn"] != arn or role["RoleId"] != receipt["role_ids"].get(arn) or {t["Key"]: t["Value"] for t in role.get("Tags", [])}.get("Experiment") != c["experiment_id"]:
                    raise Stop("Role mismatch")
                policies = api.call("iam", "list-role-policies", ["--role-name", name], cleanup=True)
                attached = api.call("iam", "list-attached-role-policies", ["--role-name", name], cleanup=True)
                if policies.get("PolicyNames") not in ([], ["cp1-scope"]) or attached.get("AttachedPolicies"):
                    raise Stop("Unexpected policies; do not detach")
                if policies.get("PolicyNames"):
                    api.call("iam", "delete-role-policy", ["--role-name", name, "--policy-name", "cp1-scope"], cleanup=True)
                api.call("iam", "delete-role", ["--role-name", name], cleanup=True)
                try:
                    api.call("iam", "get-role", ["--role-name", name], cleanup=True)
                except ApiError as exc:
                    if exc.code != "NoSuchEntity":
                        raise
                else:
                    raise Stop("Role deletion not yet confirmed")
            result = {"roles": "ABSENT", "key": "RESIDUAL_PENDING"}
    elif action == "residual":
        pending = json.loads((evidence / "schedule-key.private.json").read_text())
        if pending.get("key_arn") != c["kms_arn"]:
            raise Stop("Residual key receipt mismatch")
        deletion = pending["DeletionDate"]
        deletion_time = dt.datetime.fromtimestamp(deletion, dt.timezone.utc) if isinstance(deletion, (int,float)) else timestamp(deletion)
        if now() < deletion_time:
            raise Stop("Deletion date not reached")
        try:
            info = api.call("kms", "describe-key", ["--key-id", c["kms_arn"]], cleanup=True)["KeyMetadata"]
            status = classify_residual("SUCCESS", info["KeyState"])
        except ApiError as exc:
            status = classify_residual(exc.code)
        result = {"status": status, "key_arn": c["kms_arn"], "at": now().isoformat(),
                  "overdue": now() > deletion_time + dt.timedelta(hours=24)}
    else:
        from probes import iam_probe, lock_probe
        result = iam_probe(api, c, a) if action == "iam-probe" else lock_probe(api, c, a)
    atomic(evidence / (action + ".private.json"), result)
    return {"action": action, "evidence_saved_privately": True}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=sorted(ACTIONS | {"check-config", "check-plan"}))
    p.add_argument("--config", required=True)
    p.add_argument("--approval")
    p.add_argument("--live", action="store_true")
    p.add_argument("--plan-json")
    p.add_argument("--stack", choices=["bootstrap", "fixture"])
    p.add_argument("--mode", choices=["create", "destroy"], default="create")
    args = p.parse_args()
    c = json.loads(private_path(args.config).read_text(encoding="utf-8"))
    validate_config(c)
    if args.action == "check-config":
        print(json.dumps({"valid": True, "config_sha256": hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest(),
                          "code_sha256": code_digest()}))
    elif args.action == "check-plan":
        print(json.dumps(check_plan(json.loads(private_path(args.plan_json).read_text()), args.stack, args.mode)))
    else:
        if not args.approval:
            raise Stop("Approval file missing; no AWS call")
        a = json.loads(private_path(args.approval).read_text())
        guard(c, a, args.action, args.live)
        print(json.dumps(run_action(c, a, args.action)))

if __name__ == "__main__":
    try:
        main()
    except (Stop, KeyError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        # Never print API output, private identifiers, credentials, State or Plan.
        print("STOP: " + (str(exc) if isinstance(exc, Stop) else "Invalid input"), file=sys.stderr)
        sys.exit(2)
