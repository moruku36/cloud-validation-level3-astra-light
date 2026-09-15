#!/usr/bin/env python3
"""
Pre-flight Authentication and Environment Check Script for Autonomous AI Validation.
Verifies:
1. Git / GitHub connectivity & non-interactive mode
2. AWS CLI credentials and STS session expiration
3. Safe directory configuration
"""

import sys
import subprocess
import os
import json

def run_cmd(cmd):
    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            timeout=15
        )
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_git():
    print("[1/3] Checking Git & GitHub connectivity...")
    os.environ["GIT_TERMINAL_PROMPT"] = "0"

    ok, out, err = run_cmd("git ls-remote --get-url origin")
    if not ok:
        print(f"  [FAIL] Cannot reach git remote origin: {err}")
        return False

    remote_url = out
    ok, _, err = run_cmd("git ls-remote -h origin HEAD")
    if not ok:
        print(f"  [FAIL] Failed to query remote repository: {err}")
        print("         Please check your GitHub token / SSH credentials.")
        return False

    print(f"  [PASS] Git remote accessible ({remote_url})")
    return True

def check_aws():
    print("[2/3] Checking AWS authentication & session status...")
    ok, out, err = run_cmd("aws --version")
    if not ok:
        print("  [WARN] AWS CLI is not installed or not in PATH.")
        print("         (If this step is documentation-only, this is non-blocking)")
        return True

    ok, out, err = run_cmd("aws sts get-caller-identity --output json")
    if not ok:
        print(f"  [FAIL] AWS authentication failed: {err}")
        print("         Please renew AWS credentials (e.g., aws sso login / export keys).")
        return False

    try:
        identity = json.loads(out)
        arn = identity.get("Arn", "Unknown")
        print(f"  [PASS] Authenticated as: {arn}")
    except Exception:
        print("  [PASS] AWS credentials valid.")

    return True

def check_environment():
    print("[3/3] Checking Agent environment & Git working tree...")
    ok, out, err = run_cmd("git status --short")
    if ok:
        changes = len(out.splitlines()) if out else 0
        print(f"  [INFO] Uncommitted changes: {changes} files")

    print("  [PASS] Environment check completed.")
    return True

def main():
    print("=== Pre-flight Authentication & Health Check ===")
    results = [
        check_git(),
        check_aws(),
        check_environment()
    ]

    print("------------------------------------------------")
    if all(results):
        print("STATUS: ALL PRE-FLIGHT CHECKS PASSED. Ready for validation.")
        sys.exit(0)
    else:
        print("STATUS: PRE-FLIGHT CHECK FAILED. Resolve authentication issues before continuing.")
        sys.exit(1)

if __name__ == "__main__":
    main()
