import copy
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import c1
import probes
import tf_steps

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        acct = "246813579024"  # synthetic mock only; no AWS executor in these tests
        exp = "c1-0123456789abcdef"
        prefix = exp + "-" + acct
        self.c = dict(account_id=acct, region=c1.REGION, experiment_id=exp,
                      operator_arn=f"arn:aws:iam::{acct}:role/mock-operator",
                      backend_bucket=prefix+"-state", fixture_bucket=prefix+"-fixture",
                      state_key=f"state/{exp}/terraform.tfstate", evidence_dir=self.tmp.name,
                      roles={r:f"arn:aws:iam::{acct}:role/{prefix}-{r}" for r in ("plan","apply","cleanup")},
                      budget_jpy=500, estimated_total_jpy=212,
                      expires_at="2026-09-11T15:00:00+09:00",
                      domestic_encrypted_workspace_confirmed=True, unpriced_incremental_costs=[])
        self.at = dt.datetime(2026, 9, 11, 1, tzinfo=dt.timezone.utc)
        self.a = dict.fromkeys(c1.REQUIRED_APPROVALS, True)
        self.a.update(actions=list(c1.ACTIONS), start="2026-09-11T09:00:00+09:00",
                      status="HUMAN_APPROVED",
                      end="2026-09-11T15:00:00+09:00", code_sha256=c1.code_digest(),
                      cost_observed_at=self.at.isoformat())
        self.rebind()

    def rebind(self):
        self.a["config_sha256"] = hashlib.sha256(json.dumps(self.c,sort_keys=True).encode()).hexdigest()

    def test_no_live_flag(self):
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"preflight",False,self.at)

    def test_mock_valid(self):
        c1.guard(self.c,self.a,"preflight",True,self.at)

    def test_dummy_account(self):
        for acct in c1.BLOCKED_ACCOUNTS:
            self.c["account_id"] = acct
            with self.assertRaises(c1.Stop): c1.validate_config(self.c)

    def test_wrong_region_and_bucket(self):
        for key, value in (("region","us-east-1"),("backend_bucket","existing-production")):
            changed = dict(self.c, **{key:value})
            with self.assertRaises(c1.Stop): c1.validate_config(changed)

    def test_approval_and_code_change(self):
        self.a["budget"] = False
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"preflight",True,self.at)
        self.a["budget"] = True
        self.a["code_sha256"] = "stale"
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"preflight",True,self.at)

    def test_cost_observation_stale_and_missing_estimate(self):
        self.a["cost_observed_at"] = (self.at - dt.timedelta(minutes=16)).isoformat()
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"preflight",True,self.at)
        self.a["cost_observed_at"] = self.at.isoformat()
        self.c["estimated_total_jpy"] = None
        self.rebind()
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"preflight",True,self.at)

    def test_no_live_command_with_unapproved_example(self):
        self.a["actions"] = []
        with patch("c1.subprocess.run") as process:
            with self.assertRaises(c1.Stop):
                c1.guard(self.c,self.a,"bootstrap-apply",True,self.at)
            process.assert_not_called()

    def test_tf_apply_rejects_disabled_inputs_before_runner(self):
        root = Path(self.tmp.name)
        values = root / "vars.json"
        values.write_text(json.dumps(dict(self.c, execution_authorized=False)))
        executable = root / "terraform.exe"
        executable.write_text("not executable")
        self.c.update(bootstrap_workdir=str(root),bootstrap_tfvars=str(values),
                      terraform_executable=str(executable))
        self.a.update(terraform_binary_sha256=c1.digest(executable),
                      bootstrap_tfvars_sha256=c1.digest(values))
        runner = Mock()
        with self.assertRaises(c1.Stop):
            tf_steps.terraform_step(Mock(c=self.c),self.c,self.a,"bootstrap-apply",runner)
        runner.assert_not_called()

    def test_tf_changed_input_never_executes(self):
        root = Path(self.tmp.name)
        values = root / "vars.json"
        values.write_text("{}")
        executable = root / "terraform.exe"
        executable.write_text("not executable")
        self.c.update(fixture_workdir=str(root),fixture_tfvars=str(values),
                      terraform_executable=str(executable))
        self.a.update(terraform_binary_sha256=c1.digest(executable),
                      fixture_tfvars_sha256="wrong")
        runner = Mock()
        with self.assertRaises(c1.Stop):
            tf_steps.terraform_step(Mock(c=self.c),self.c,self.a,"fixture-plan",runner)
        runner.assert_not_called()

    def test_saved_plan_requires_exact_approval(self):
        root = Path(self.tmp.name)
        work = root / "bootstrap"
        work.mkdir()
        source = Path(__file__).resolve().parents[1] / "bootstrap"
        for p in source.iterdir():
            if p.suffix == ".tf" or p.name == ".terraform.lock.hcl":
                shutil.copy2(p, work / p.name)
        values = root / "vars.json"
        values.write_text(json.dumps(dict(self.c, execution_authorized=True)))
        executable = root / "terraform.exe"
        executable.write_text("not executable")
        (work / "reviewed.tfplan").write_text("mock saved plan")
        self.c.update(bootstrap_workdir=str(work),bootstrap_tfvars=str(values),
                      terraform_executable=str(executable),profiles={"operator":"mock"})
        self.a.update(terraform_binary_sha256=c1.digest(executable),
                      bootstrap_tfvars_sha256=c1.digest(values),terraform_bound_reviewed=True,
                      terraform_request_reservation={k:1 for k in c1.LIMITS},
                      bootstrap_plan_sha256="wrong",bootstrap_plan_approved=True)
        api=c1.Aws(self.c,"mock",runner=Mock())
        runner=Mock()
        with self.assertRaises(c1.Stop):
            tf_steps.terraform_step(api,self.c,self.a,"bootstrap-apply",runner)
        runner.assert_not_called()

    def test_multipart_stops_before_delete(self):
        api = Mock(c=self.c,dir=Path(self.tmp.name))
        api.call.side_effect = [{"LocationConstraint":c1.REGION},
            {"TagSet":[{"Key":"Experiment","Value":self.c["experiment_id"]}]},
            {"Uploads":[{"Key":"unknown","UploadId":"unknown"}]}]
        with self.assertRaises(c1.Stop):
            c1.purge(api,self.c["fixture_bucket"],{"created_buckets":[self.c["fixture_bucket"]]})
        self.assertFalse(any(call.args[1].startswith("delete") for call in api.call.call_args_list))

    def test_wrong_tag_stops_before_inventory(self):
        api=Mock(c=self.c,dir=Path(self.tmp.name))
        api.call.side_effect=[{"LocationConstraint":c1.REGION},{"TagSet":[{"Key":"Experiment","Value":"other"}]}]
        with self.assertRaises(c1.Stop):
            c1.purge(api,self.c["fixture_bucket"],{"created_buckets":[self.c["fixture_bucket"]]})
        self.assertEqual(api.call.call_count,2)

    def test_unknown_cost_blocks(self):
        self.c["unpriced_incremental_costs"] = ["audit"]
        self.rebind()
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"preflight",True,self.at)

    def test_overnight(self):
        self.a.update(start="2026-09-11T23:00:00+09:00",end="2026-09-12T02:00:00+09:00")
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"preflight",True,self.at)

    def test_stop_new_work_keep_cleanup(self):
        late = self.at + dt.timedelta(hours=5)
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"iam-probe",True,late)
        c1.guard(self.c,self.a,"cleanup-backend",True,late)

    def test_residual_separate_approval(self):
        with self.assertRaises(c1.Stop): c1.guard(self.c,self.a,"residual",True,self.at)

    def test_public_evidence_forbidden(self):
        with self.assertRaises(c1.Stop): c1.private_path(c1.REPO / "raw.tfstate")

    def test_denial_classification(self):
        self.assertEqual(c1.classify_denial("SUCCESS"),"FAIL_UNEXPECTED_ALLOW")
        self.assertEqual(c1.classify_denial("AccessDenied"),"EXPECTED_DENY")
        for value in ("NoSuchKey","ExpiredToken","TRANSPORT_UNKNOWN"):
            self.assertEqual(c1.classify_denial(value),"UNKNOWN")

    def test_lock_classification(self):
        self.assertEqual(c1.classify_lock(0,"","abc"),"FAIL_UNEXPECTED_LOCK_BYPASS")
        self.assertEqual(c1.classify_lock(1,"AccessDenied","abc"),"UNKNOWN")
        self.assertEqual(c1.classify_lock(1,"Error acquiring the state lock PreconditionFailed abc","abc"),
                         "EXPECTED_LOCK_CONFLICT")

    def test_pending_is_residual(self):
        self.assertEqual(c1.classify_residual("SUCCESS","PendingDeletion"),"RESIDUAL_PENDING")
        self.assertEqual(c1.classify_residual("AccessDeniedException"),"UNKNOWN")
        self.assertEqual(c1.classify_residual("NotFoundException"),"ABSENT")

    def test_plan_outside_and_replacement(self):
        for addr, acts in (("aws_db_instance.prod",["create"]),("aws_s3_bucket.fixture",["delete","create"]),
                           ("aws_s3_bucket.fixture",["update"])):
            plan = {"resource_changes":[dict(mode="managed",address=addr,change={"actions":acts})]}
            with self.assertRaises(c1.Stop): c1.check_plan(plan,"fixture")
        plan = {"resource_changes":[dict(mode="managed",address="aws_s3_bucket.fixture",change={"actions":["delete"]})]}
        self.assertTrue(c1.check_plan(plan,"fixture","destroy")["human_review_required"])

    def test_account_identity_mock(self):
        runner = Mock(return_value=Mock(returncode=0,stdout=json.dumps({"Account":"999999999999","Arn":"bad"})))
        api = c1.Aws(self.c,"mock",runner=runner)
        with self.assertRaises(c1.Stop): api.identity(self.c["operator_arn"])
        self.assertEqual(runner.call_count,1)
        env = runner.call_args.kwargs["env"]
        self.assertEqual(env["AWS_EC2_METADATA_DISABLED"],"true")

    def test_quantity_stop_before_command(self):
        runner = Mock()
        api = c1.Aws(self.c,"mock",runner=runner)
        c1.atomic(api.ledger,{k:v for k,v in c1.LIMITS.items()})
        with self.assertRaises(c1.Stop): api.call("sts","get-caller-identity")
        runner.assert_not_called()

    def test_absence_does_not_accept_denial(self):
        api = Mock(c=self.c)
        api.call.side_effect = c1.ApiError("AccessDenied")
        with self.assertRaises(c1.Stop): c1.absent_bucket(api,self.c["fixture_bucket"])

    def test_delete_requires_creation_receipt(self):
        api = Mock(c=self.c)
        with self.assertRaises(c1.Stop): c1.purge(api,self.c["fixture_bucket"],{"created_buckets":[]})
        api.call.assert_not_called()

    def test_delete_requires_inventory_approval(self):
        api = Mock(c=self.c, dir=Path(self.tmp.name))
        api.call.side_effect = [
            {"LocationConstraint":c1.REGION},
            {"TagSet":[{"Key":"Experiment","Value":self.c["experiment_id"]}]},
            {}, {"Versions":[{"Key":"x","VersionId":"1","Size":2}]}
        ]
        with self.assertRaises(c1.Stop):
            c1.purge(api,self.c["fixture_bucket"],{"created_buckets":[self.c["fixture_bucket"]]})
        self.assertFalse(any(call.args[1].startswith("delete") for call in api.call.call_args_list))

    def test_purge_includes_delete_markers(self):
        rows=[{"Key":"x","VersionId":"1","Size":2},{"Key":"x","VersionId":"2"}]
        api=Mock(c=self.c,dir=Path(self.tmp.name))
        api.call.side_effect=[
            {"LocationConstraint":c1.REGION},
            {"TagSet":[{"Key":"Experiment","Value":self.c["experiment_id"]}]},
            {}, {"Versions":[rows[0]],"DeleteMarkers":[rows[1]]}, {}, {}, {}, {},
            c1.ApiError("NoSuchBucket")]
        h=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
        result=c1.purge(api,self.c["fixture_bucket"],{"created_buckets":[self.c["fixture_bucket"]],
                       "purge_inventory_sha256":{self.c["fixture_bucket"]:h}})
        self.assertEqual(result["status"],"ABSENT")
        self.assertEqual(sum(call.args[1]=="delete-object" for call in api.call.call_args_list),2)

if __name__ == "__main__":
    unittest.main()
