"""Create private binding files offline. Never runs Terraform or AWS."""
import argparse
import json
from pathlib import Path
from c1 import (validate_config, private_path, atomic, Stop, REGION, expected_account,
                resolved_operator_role_arn)

def materialize(c, out):
    validate_config(c)
    out = private_path(out)
    out.mkdir(parents=True, exist_ok=True)
    common = {"account_id": expected_account(c), "operator_arn": resolved_operator_role_arn(c)}
    common.update({k: c[k] for k in ("experiment_id", "expires_at")})
    common["execution_authorized"] = False
    atomic(out / "bootstrap.tfvars.json", common)
    if c.get("kms_arn", "").startswith("arn:aws:kms:"):
        atomic(out / "fixture.tfvars.json", dict(common, kms_arn=c["kms_arn"]))
        # JSON is valid backend config syntax. Native locking, default workspace only.
        backend = dict(bucket=c["backend_bucket"], key=c["state_key"], region=REGION,
                       encrypt=True, kms_key_id=c["kms_arn"], use_lockfile=True,
                       allowed_account_ids=[expected_account(c)], max_retries=1)
        atomic(out / "backend.hcl.json", backend)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    materialize(json.loads(private_path(args.config).read_text()), args.out)
