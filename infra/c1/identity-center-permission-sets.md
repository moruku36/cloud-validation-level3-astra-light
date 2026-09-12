# C-1 Identity Center Permission Set候補

全案は未承認。`PowerUserAccess` / `AdministratorAccess` は採用しない。custom inline policyを優先し、対象account・固定名・段階を限定する。Permission Set作成だけでは対象accountに権限は生じず、assignment時に予約IAM Roleが作られる。[custom permissions仕様](https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsetcustom.html)

## A. Preflight専用（推奨する最初の1 set）

|Action|Resource候補|制限|
|---|---|---|
|`sts:GetCallerIdentity`|`*`|AWS仕様上、明示Allowがなくてもidentityを返す。目的上の呼出しだけを記録|
|`s3:GetBucketLocation`|固定State/fixture bucket ARN各1|一覧、object read/writeなし。`AccessDenied`も衝突としてFAIL|
|`iam:GetRole`|固定plan/apply/cleanup role ARN各1|Role一覧、policy read、writeなし|

KMS、Billing、Organizations、Identity Center管理、CloudTrail、Terraform Plan、writeを含めない。既存最大6 API、retry 0の承認は新Identity Center Roleへ自動継承しない。

具体候補は[Preflight inline policyテンプレート](identity-center-preflight-policy.example.json)。プレースホルダーはassignment前にprivate固定し、公開repoへ実account ID・資源名を保存しない。

## B. Bootstrap Plan候補

Preflightとは別Permission Setを推奨する。固定bootstrap Stateがlocalかつ新規構成なら、Terraform providerのcredential/account検証とempty State refreshを要する。ただしprovider 6.14.1の内部API集合は公式資料だけで有限に確定できないため、Plan前にdebugの秘密漏えいを避けた方法で候補APIと最大回数を確定できなければ停止する。

候補readは固定S3名への各bucket設定read、固定3 Roleへの`GetRole`/inline・attached policy metadata read、作成済み対象がある場合だけKMS `DescribeKey`/policy/rotation/tag read。KMS alias衝突確認を追加するなら `kms:ListAliases` は一覧範囲を広げるため、コード・API・証跡の別承認が必要で、現コードはaliasを作らない。Planに不要なCreate/Put/Delete/Attach/Tag/PassRole/AssumeRoleは含めない。

## C. Bootstrap apply / cleanup候補

後続の別承認対象。候補は固定名S3/KMS/3 IAM Roleと付随設定のCreate/Get/Put/Tag、承認Plan apply、作成receiptへ一致する対象だけのDelete、KMS 7日ScheduleKeyDeletionである。Identity Center管理権限やOrganizations権限をC-1 apply Roleへ混ぜない。実Action/resource/conditionはPlanとAPI量確定後に別文書化し、今回のPermission Setへ入れない。

## 同一setと分離setの比較

|案|最小権限|運用|予約IAM Role数|cleanup/guard|
|---|---|---|---|---|
|1 setを段階更新|時点ごとにpolicyを変更するため誤付与・provision遅延リスク|assignmentは少ないが毎段階変更・再承認|対象accountに1|guardのRole名は一定。ただしpolicy hash/provision証跡が毎回必要|
|Preflight/Plan/Apply/Cleanup分離|最も明確。各Roleは段階権限だけ|Permission Set/assignment/Roleが増える|最大4|Roleごとのprivate bindingとguard拡張が必要。解除順も増える|
|Preflight 1＋後続Operator 1|初回readを厳格分離し、後続は別承認|中程度|2|現guardは単一Role前提。段階切替時にprivate configと承認を更新|

**現時点の推奨はPreflight専用1 setだけを先に設計し、Plan/apply setは作らない。** 現guardは1つの完全Role名を拘束するため、複数set採用時は各段階で新config承認、又は別のコード修正が必要となる。Permissions boundaryは権限を付与せず上限を設ける。customer-managed boundaryは対象accountに同名policyを事前作成する追加資源となるため、Preflightではinline policyの固定Action/Resourceで足りるかを先に審査する。[boundary仕様](https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsetcustom.html#permissions-boundaries)
