# C-1 Identity Center 現状態確認・有効化ゲート

## 次工程G-IC1：Console read-only確認

操作主体はユーザー本人。既存のConsole認証でログインできる場合だけ、次の画面を閲覧する。**Enable/Create/Change/Delete/Assign/Register/Set up/Accept invitationは押さない。** login自体を含め本工程では未実施で、次工程の個別承認対象である。

|画面経路|確認項目|公開回答|
|---|---|---|
|AWS Organizations → AWS accounts / Settings|Organization有無、management/member、all features、delegated admin|`なし` / `あり・management` / `あり・member` / `不明`|
|IAM Identity Center、Regionを東京に固定 → Dashboard / Settings → Management|instance有無・種別、primary/additional Region、暗号化key種別|`なし` / `organizationあり` / `accountあり` / `不明`、Region `東京` / `東京以外` / `未確認`|
|Settings → Identity source / Authentication|Identity Center directory、external IdP、AD、MFA方式|分類だけ。user/email/Directory IDは記録しない|
|Users / Groups|既存有無とC-1専用候補を追加可能か|件数分類と `追加可能/不可/未確認`|
|Multi-account permissions → Permission sets|既存set、同名衝突、session、boundary|名称・ARNを公開しない|
|Multi-account permissions → AWS accounts → 対象account|assignment有無と追加可能性|`可能/不可/未確認`。account IDは公開しない|
|Settings → AWS access portal|portal既存有無|`あり/なし/未確認`。URLはprivate|
|CloudTrail → Event history / Trails（東京）|既存management event、trail/Lake/S3/CloudWatch配信有無|`Event historyのみ/既存配信あり/未確認`。宛先名はprivate|
|IAM/管理権限表示|Organizations/Identity Center変更を行える主体の有無|`対応可能/追加権限必要/未確認`。principal名はprivate|

画面閲覧でもaccount構成・identity metadataへのアクセスとなり、既存Console sessionとread権限が必要である。誤操作、Region誤認、機密画面の公開保存をリスクとし、スクリーンショット原本は国内private領域、公開repoには上記分類と確認日時だけを保存する。account ID、メール、ARN、portal URL、user/group/set名をチャットへ貼らない。

## 独立ゲート

|G|主体・対象/必要権限|副作用・費用|成功条件 / rollback・即時不可|証跡 / 次承認|
|---|---|---|---|
|1 現状態read|本人、上記Console画面、既存read権限|metadata閲覧。設定変更なし|分類完了。rollback不要|redacted分類。次は構成確定承認|
|2 構成確定|本人＋レビュー、文書のみ|なし|org/instance/Region/source/保持を確定|決定票。変更gateを個別承認|
|3 Organizations|既存管理principal、CreateOrganization等|management account化、all features、service-linked role、SCP、検証mail。Organizations自体無料|想定状態一致。削除はmember/policy等の前提があり即時不能の場合あり|private org証跡。instance gate承認|
|4 instance|management principal、Identity Center enable権限|東京instance、Identity Store、portal、service-linked roles。AWS owned keyは追加料金なし|single-region/東京/key/source一致。削除は不可逆で既存利用・sessions/logに残存|instance分類。identity gate承認|
|5 user/group|Identity Center directory admin|PII、招待/確認mail、user/group/membership|private user 1/group 1。削除でinstance storeから消えるがmail/logは即時消えない|ID/時刻private。Permission Set承認|
|6 Permission Set|SSO admin、custom inline policy|set metadata。まだtarget Roleなし|Preflight Action/Resource/session 1hだけ|policy JSON/hash private。assignment承認|
|7 assignment|SSO account assignment＋target provisioning権限|予約IAM Role/policy 1、portal表示|user/group→target→set一致。解除でRole削除だがactive sessionは期限まで残り得る|assignment/Role完全名private。MFA承認|
|8 MFA|本人＋directory admin|device登録、回復情報|Always On、FIDO2/TOTP、回復手順。device紛失は即時rollback困難|device種別だけ。CLI profile承認|
|9 `aws configure sso`|国内PCの本人|`~/.aws/config`へsso-session/profile、browser登録|長期keyなし、東京issuer、対象account/set。profile削除でrollback|値はprivate。login承認|
|10 `aws sso login`|国内PCの本人|browser認証、OIDC/token cache、CloudTrail/sign-in、session開始|MFA成功、token private。logoutしても取得済みRole sessionは期限まで残り得る|時刻/成否だけ公開。binding承認|
|11 offline binding/guard|本人＋AI支援、local file readだけ|private config更新。AWS 0|SSO profile/account/Permission Set/完全Role名、東京、retry、evidence条件PASS|safe guard結果。preflight再承認|
|12 最大6 API|本人＋AI支援、STS1/S3 2/IAM3|管理metadata、少量request、30分枠|全6結果と回数確定。失敗で即停止|private raw/public分類。Bootstrap Planはさらに別承認|

各gateは前gateの証跡と**そのgate固有の人間承認**が必要。rollback操作も自動承認しない。Identity Center/Organizations、identity、assignment、Role、CloudTrail、token cacheは既存S3 2/KMS 1/IAM role 3へ数えない。

次工程はG-IC1だけ。許可候補は上表の画面閲覧と分類記録、禁止はEnable/Create/Edit/Delete/Assign/Provision/Register、Region変更、Organizations招待/作成、MFA登録、CLI/API、profile/loginである。
