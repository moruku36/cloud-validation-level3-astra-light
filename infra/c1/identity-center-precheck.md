# C-1 IAM Identity Center方式：選定・有効化前審査

日付：2026-09-13。起点PR #22 head `2edc99a652f12780e802008ea009946a9a29e1e1`。本書は設計候補であり、Console操作、Organizations/Identity Center変更、identity、Permission Set、assignment、profile、loginを承認しない。

## 結論と最小構成候補

第一候補は **東京のorganization instance、single-region、AWS owned key、Identity Center directory、専用private user＋専用group、C-1 Preflight専用custom Permission Set、対象account 1件へのgroup assignment、MFA Always On、permission-set session 1時間、AWS CLI v2 SSO token provider** とする。AWSアカウントへのSSOとPermission Setはorganization instanceだけが対応し、account instanceは使えないためである。[instance比較](https://docs.aws.amazon.com/singlesignon/latest/userguide/identity-center-instances.html)

既存organization instanceが東京以外にある場合、primary Regionは直接変更できず、削除・再作成が必要となる。既存利用を破壊し得るため東京へ独断で移さず、既存instance継続又は別案を再判断する。[organization instance仕様](https://docs.aws.amazon.com/singlesignon/latest/userguide/organization-instances-identity-center.html)

|構成要素|未承認候補|理由・条件|
|---|---|---|
|instance|organization / `ap-northeast-1` / single-region|account accessに必須。standaloneならOrganizations all-features新設を伴う|
|暗号化|AWS owned key|既定・追加料金なし。customer managed KMS keyは作らない|
|identity source|Identity Center directory|外部IdP/ADが既存なら変更せず再審査。default directoryはDirectory ServiceのADを作らない|
|identity|private operator user、専用group 1|実メール等はprivate管理。group assignmentで後の入替を容易にする|
|権限|まずPreflight custom Permission Set 1|書込み、一覧、KMS、請求を含めない。Plan/apply用は別gate|
|assignment|専用group→対象account 1→Preflight set|`AWSReservedSSO_...` Role 1個が対象accountへ増える|
|認証|MFA Always On、FIDO2又はTOTP|Identity Center directoryなら設定可能。登録操作は別承認|
|session|Permission Set 1時間|公式範囲1–12時間、default 1時間。portal sessionは別設定|
|CLI|AWS CLI v2、SSO token provider|長期keyを作らず、ブラウザ認証と自動refreshに対応|
|証跡|CloudTrail Event historyとredacted画面記録|生ID、メール、URL、ARNはprivate。公開は状態分類だけ|
|終了|継続利用を推奨候補|削除・再作成でRole suffixが変わり、既存参照や復旧に影響。最終判断は有効化前|

## 公式仕様確認（2026-09時点）

|確認点|公式確認結果|有効化前の扱い|
|---|---|---|
|standalone account|organization instanceを選ぶと、そのaccountをmanagement accountとする新Organizationを作成する。Organizationsはall featuresが既定|既存契約・請求・SCP影響をConsoleで確認し、Organizations作成を個別承認|
|既存Organizations|organization instanceはmanagement accountでのみ有効化し、1 management accountにつき1 instance|memberならmanagement側担当・権限が必要。勝手にaccount instanceへ代替しない|
|instance差|organizationは全機能・multi-account permissions・AWS account portal対応。account instanceはPermission Set/AWS account access非対応|account instanceしかない場合はC-1経路不成立|
|primary Region|作成Regionから直接変更不可。変更はinstance削除後に別Regionで再作成|東京以外の既存instanceは阻害事項|
|single-region/key|primary 1 Region、追加Regionなし、AWS owned key。Permission Setsは有効で後から無効化不可|customer KMSは不要。追加Regionは範囲外|
|作成・影響|organization/instance、Identity Store、access portal、`AWSServiceRoleForSSO`。assignment時に予約IAM Roleとpolicy。既存IAM user/role/policyは変更しない|全て既存C-1のS3 2/KMS 1/role 3とは別資源・永続設定|
|Directory/OIDC|default Identity Center directoryを利用。CLI設定・login時にSSO OIDC token providerとlocal token cacheを使用|AD/外部IdPは作らない。OIDC/profile/cacheは別承認|
|監査|Identity Center、Identity Store、OIDC、portal、sign-in等をCloudTrailが記録。Event historyは直近90日のRegion別management events|既存trail/S3/CloudWatch/Lakeへの配信・費用は現状態確認まで未確認|
|保存地域|directory構成、Permission Sets、applications、assignments、Identity Store user/groupは有効化Regionに保存。東京はdefault-enabled Region|browser/IdP、Organizations、CloudTrail配信、受信メール先を含むend-to-end国内保存は公式資料だけでは未確認。追加control-plane metadata例外の承認が必要|
|メール経路|初期招待、確認、password reset、OTP等でSESを使用。東京は公式cross-Region代替表の対象外|実送信・受信先保存は別承認。private emailはrepoに保存しない|
|料金|IAM Identity CenterとOrganizationsは追加料金なし。AWS owned keyも追加料金なし。CloudTrail Event history閲覧は無料|trail先S3/CloudWatch、CloudTrail Lake、AD、外部IdP、通信/MFA device等は別料金又は未確認U|
|MFA|Identity Center store/Managed AD/AD Connectorで利用可。外部IdPではIdentity Center MFA非対応。FIDO2/TOTP等をCLI v2にも使用可|identity source確認前に設定方式を確定しない|
|session|Permission Set role sessionは1–12h、default 1h。portal interactive sessionは15分–90日、default 8hで別管理|C-1はrole session 1h案。portal側も1hへ短縮するか要回答|
|CLI|SSO token providerが推奨。`sso-session`にstart/issuer URLとSSO Region、profileにaccount/roleを設定|`aws configure sso`、browser auth、login、cache生成は未承認|
|Role命名/削除|assignmentで `AWSReservedSSO_<PermissionSet>_<suffix>` を予約pathに作成。全assignment削除でRoleも削除され、再作成時suffixが変わる|固定guardへ完全Role名をprivate bindするのはassignment後。削除時は参照切れに注意|
|instance削除|Permission Sets、applications、assignments、Identity Center storeのuser/groupを不可逆削除。追加Regionは先に除去|active role session、service-linked role、CloudTrail、local cacheの即時消滅は保証されないため別確認|

公式根拠：[有効化](https://docs.aws.amazon.com/singlesignon/latest/userguide/enable-identity-center.html)、[Region保存](https://docs.aws.amazon.com/singlesignon/latest/userguide/regions.html)、[暗号化](https://docs.aws.amazon.com/singlesignon/latest/userguide/encryption-at-rest.html)、[CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)、[MFA](https://docs.aws.amazon.com/singlesignon/latest/userguide/mfa-configure.html)、[Role命名](https://docs.aws.amazon.com/singlesignon/latest/userguide/referencingpermissionsets.html)、[削除](https://docs.aws.amazon.com/singlesignon/latest/userguide/delete-config.html)、[料金](https://aws.amazon.com/iam/identity-center/faqs/)、[Organizations料金](https://docs.aws.amazon.com/organizations/latest/userguide/pricing.html)、[CloudTrail](https://docs.aws.amazon.com/singlesignon/latest/userguide/logging-using-cloudtrail.html)。

## C-1承認範囲との差分

|追加対象|数量・状態候補|既存C-1との関係|cleanup/保持|
|---|---|---|---|
|Organizations|standalone時1 organization＋service-linked role/SCP等|新しいaccount全体設定|継続推奨候補。削除は別の高影響操作|
|Identity Center|organization instance 1、Identity Store/access portal|永続control plane|継続案又は不可逆削除案を事前選択|
|identity|user 1、group 1、membership 1|個人情報をprivate管理|C-1後disable/remove又は継続|
|Permission Set/assignment|最初はPreflight set 1＋assignment 1|既存3 Roleとは別に予約IAM Role 1|assignment解除でRole削除、suffix変化に注意|
|CLI|SSO profile/sso-session 1、token cache|国内PC local設定|logout＋profile/cache削除は別承認|
|監査/metadata|CloudTrail events、portal/OIDC/sign-in metadata|既存限定metadata例外より範囲増|Event historyは90日。既存trailの保持は現状態依存|

**継続利用案（推奨候補）**は今後も短期認証を再利用でき、Role suffix/identity再作成を避けるが、user/group/assignment/portalを継続管理する責任が残る。**C-1後削除案**は永続面を減らす一方、instance dataは不可逆、Organizationやログ/cache/service-linked roleは別cleanup、active role sessionは最大session期限まで残り得る。どちらも今回承認しない。

## 承認マトリクス

|項目|状態|
|---|---|
|Identity Center方式の採用方針、詳細設計・有効化前審査|承認済み|
|Organizations作成・変更、Identity Center instance有効化|未承認|
|user/group/Permission Set/assignment、MFA登録|未承認|
|CLI SSO profile、SSO login、token cache|未承認|
|新固定版コード、AWS API/preflight|未承認|
|Terraform Plan/apply/cleanup|未承認|

正式自己評価66/66/66、設計不合格、LC1未採点、C全体移行保留を維持する。
