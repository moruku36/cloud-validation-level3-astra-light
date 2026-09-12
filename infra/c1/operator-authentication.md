# C-1 Operator認証ガード（修正版）

固定候補：PR #21 head `7e9b133c750db93953e0e5e260c9c4c0a65a5a8d` を起点とする本PRの `infra/c1`。旧方式はcaller ARN完全値をSTS前に要求し、可変session名を含むSTS ARNとIAM Role ARNを混同していた。本修正は期待accountを維持し、事前にはprincipal種別・role名・認証方式を拘束し、実callerは最初のSTS応答後に照合する。コード修正は承認済みだが、新固定版とAWS API実行は未承認である。

## private入力とoffline/live境界

|入力・条件|offline `check-config`|STS後|
|---|---|---|
|`expected_account_id`|12桁・dummy拒否|Account完全一致|
|`expected_partition` / `expected_principal_type`|`aws` / `assumed-role`固定|ARN構造と一致|
|`expected_role_name`|完全なIAM role名の形式|assumed-roleのrole segmentと完全一致|
|`expected_sso_permission_set_name`|SSO時のみ必須。予約role名 `AWSReservedSSO_<permission-set>_<16hex>` との対応を検査|直接は使わず、上記完全role名を検査|
|`expected_authentication_type`|`sso` / `assume-role` / `credential-process`のschema。後者は停止扱い|承認種別との一致|
|`aws_profile`|section存在と認証方式分類。接続・credential取得なし|実際の認証可否はSTSで初確認|
|その他|東京、retry 1 attempt、実験ID、固定5名称、repo外証跡先、国内本人管理PC・暗号化・同期外・ACL|STS成功後も後続APIは別承認範囲|

offline成功はSSO session有効性、実caller、Role実在、権限を証明しない。これらは `STS実行時に確認` のままとする。Terraformへ必要なIAM Role ARNは、SSOでは固定予約path・privateの完全role名、AssumeRoleではlocal configの`role_arn`から内部生成する。手入力の完全caller ARNは廃止した。

## 認証方式別の扱い

- **IAM Identity Center / SSO**：local profileのaccountとPermission Set名をprivate期待値へ完全一致させる。予約IAM Roleの完全名も別に拘束する。SSO loginは行わず、有効性は未確認とする。Identity CenterのRole名とpathは[AWS公式形式](https://docs.aws.amazon.com/singlesignon/latest/userguide/referencingpermissionsets.html)だけを許容する。
- **AssumeRole**：local `role_arn`を構造parseし、accountと終端role名を完全一致させる。source profileは設定済みSSO候補だけを許容し、秘密値を読まない。pathはIAM ARNで検査し、STS callerでは終端role名だけを照合する。
- **credential_process等**：schema上は分類するが、commandを実行せず `UNDETERMINED` 相当で停止する。利用には別設計・承認が必要。
- **静的access key直結**：key値を読まず、credentials sectionのkey存在だけで不許可。IAM user利用を許可しない。
- **root / IAM user / federated-user / 未知形式**：STS照合で常に拒否する。

現在のPCでは非通信・非表示のmetadata検査だけを行い、profile 2件はいずれも静的認証分類だった。許可候補は0件、AWS通信は0回。profile名、設定値、credentialは表示・保存していない。したがって既存Operator Roleの実在は **UNDETERMINED** である。

## STS後の固定照合順

1. `GetCallerIdentity`成功。
2. Accountがprivate期待値と完全一致。
3. ARNをpartition / service / account / resource segmentsへ構造parse。
4. `assumed-role`だけを許可。
5. role segmentを承認済み完全role名へ完全一致。
6. session segmentを固定ASCII形式 `^[A-Za-z0-9_+=,.@-]{2,64}$` で検査。
7. root、user、federated-user、path/percent encoding、欠落・余分segment、未知serviceを拒否。
8. 成功後だけS3・IAM不存在確認へ進む。

照合結果の公開出力はaccount一致、principal分類、role一致、session形式だけで、Account・ARN・profile・role名を含めない。[STSのassumed-role ARN形式](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html)に従い、部分一致は使わない。

## Operator Roleがない場合の候補（文書案のみ）

目的はC-1のpreflight、bootstrap Plan/apply、fixture Plan/apply、probe、cleanupを承認ゲートごとに分離すること。信頼元は既存の組織管理SSO principal又は既承認の短期認証Roleに限定し、外部ID・session tag・source identity・MFAを利用可能性と運用経路から確定する。推奨最大sessionは1時間の未承認案で、6時間枠中は再認証時にも同じguardを通す。

権限は (1) preflightのSTS/S3 2名/IAM 3名read、(2) bootstrap Plan read、(3)承認Planの限定create/update、(4)fixture/probe、(5)作成由来だけのcleanup に分ける。最初のRole作成者は既存のaccount管理責任者が担い、AIは作成者を仮定しない。bootstrap用の一時権限を使う場合は対象ARN/prefix、期限、作成receiptを固定し、bootstrap後に失効・削除を別承認で確認する。静的keyは作らない。

|候補|利点|制約|
|---|---|---|
|Terraform|review可能だが、Role作成前のState・実行principal・Plan承認が別途必要|
|CloudFormation|change setで差分確認可能。stack/実行Role/cleanupを追加管理|
|Console|初回bootstrapに使えるが、再現性と証跡を手動補完|

方式選定、trust/permission policy、MFA、session条件、作成者、作成操作、profile変更、SSO loginはすべて別承認事項である。既存の許可可能profileがないことは確認したが、Role新設が必要かはAWS未確認のためまだ断定しない。

## 承認状態

|項目|状態|
|---|---|
|Operator認証ガード修正、Role設計文書|承認済み|
|本PRの新固定版コード|未承認|
|AWS API再実施、Role作成、profile変更、SSO login|未承認|
|Plan、apply、probe、cleanup|未承認|

旧PR #18固定版への実行条件は本変更へ自動継承しない。66/66/66点、設計不合格、LC1未採点、C全体移行保留を維持する。
