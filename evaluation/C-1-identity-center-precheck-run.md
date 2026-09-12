# C-1 IAM Identity Center認証経路：有効化前審査記録

日付：2026-09-13。起点PR #22 head `2edc99a652f12780e802008ea009946a9a29e1e1`、比較先 `codex/c1-operator-auth-guard`。直接依存#22、間接#21→#20→#19→#18→#17→#16→#15。全PR OPEN・未マージを再確認した。

提出先：[PR #23](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/23)。成果物変更SHA `5afdc9cd46faba0bb9225c8dbd2e4e0497f0e2ce`。

IAM Identity Centerを第一候補とする方針と本設計審査だけ承認済み。公式仕様からAWS account accessにはorganization instanceが必要で、standaloneならOrganizations all-features新設を伴い、member accountだけでは作れないと判定した。推奨候補は東京single-region、AWS owned key、default Identity Center directory、専用user/group、Preflight専用custom Permission Set、MFA Always On、1時間session、CLI v2 SSO token providerである。

AWS上のOrganizations/instance/Region/identity/assignment/portal/管理権限/監査設定は全て未確認。次はConsole read-only分類を個別承認して実施する。Organizations/Identity Center/identity/Permission Set/assignment/MFA/profile/login、新固定版、AWS API、Plan/apply/cleanupは未承認・未実施。

AWS接続/API 0回、Console操作0回、profile/credential変更0、資源作成・変更・削除なし。Identity Center/Organizationsは追加料金なし、AWS owned keyも追加料金なしと公式確認。既存trail配信、S3/CloudWatch/Lake、AD/外部IdP、通信等の費用Uは未確認。モデル識別、トークン、料金、実作業時間は不明。66/66/66点不合格、LC1未採点、C全体移行保留を維持する。
