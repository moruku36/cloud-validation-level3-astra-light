# C-1 CP2：実行ゲートとread-only preflight候補

固定実装：PR #18 head `f5b8982010a2420e0084cf700db6e0d2c695a640` の `infra/c1`。承認記録：[C-0 CP2](../../experiments/C/C-0/approval-2026-09-12.md)。本書は手順と将来の個別承認単位を固定する文書で、クラウド操作許可ではない。

## 固定ゲート

各ゲートは直前までの証跡が揃い、そのゲート固有の人間承認を得た場合だけ開始する。失敗・不明・タイムアウトでは後続へ進まず、許可範囲を広げない。

|G|工程・現在状態|必要入力|そのゲートで許可する候補操作|停止条件|取得する証跡|
|---|---|---|---|---|---|
|G0|文書承認反映：今回完了|2026-09-12の承認要約、固定SHA、依存PR|公開文書・PR・Issue更新だけ|秘密/実ID混入、承認内容の拡大|承認項目、固定SHA、PR head/base、remote blob一致|
|G1|実環境read-only preflight：**未承認・次候補**|private account ID/operator ARN/profile、experiment ID、計算した2 bucket名/3 role名、国内PC/経路、1回6 API attemptの承認、開始/終了絶対時刻|下表のSTS 1、S3 2、IAM 3だけ。作成/変更/削除/請求API/一覧取得なし|caller/account/role不一致、東京以外、名前の既存又はAccessDenied/通信不明、想定外endpoint/proxy、権限/U/保存先不明、API上限到達|rawは国内private。公開可：固定コードhash、実IDを塩付きhash等で置換した照合結果、各APIの成功/期待NotFound/未確認、時刻、呼出数|
|G2|bootstrap Plan作成：未承認|G1 PASS、固定コード/input/binary hash、operatorの必要権限とTerraform予約量/U、local State保存先|local backendのinit、AWS providerのreadを伴うbootstrap Plan保存。applyなし|PlanにS3 1/key 1/role 3＋付随設定以外、update/import/replacement/既存対象、東京外、500円根拠不足|private Plan/State、Plan SHA、非機密resource/action集計、API予約/費用見込|
|G3|bootstrap Plan人間承認：未承認|G2の完全Plan、操作/権限/価格/U、開始時刻案|private Planの人間レビューと承認記録だけ|生Planを公開、差分/U/権限が説明不能|承認者役割、日付、Plan/code/input SHA、許可action、失効条件|
|G4|bootstrap apply：未承認|G3承認、実行開始/終了JST、15分以内の費用評価、本人在席|承認Planそのもののapply。State bucket 1/key 1/role 3と付随設定だけ|Plan/hash/caller不一致、見込300円以上又は総額500円説明不能、5h/同日余裕不足、部分失敗/未知応答|private local State/Plan/CLI結果、作成時刻/ID/RoleId、費用/数量、非機密作成集計|
|G5|fixture Plan作成：未承認|G4作成由来binding、実key ARN、承認backend config、空fixture State、Terraform予約量|remote S3 backend initとfixture Plan。作成/変更なし（backendのState初期化に必要なS3/KMS操作は発生し得る）|既存State/backend、force-copy要求、別bucket/key/account/region、fixture 1以外の差分|private backend metadata/Plan/State、hash、API/費用/対象集計|
|G6|fixture Plan人間承認：未承認|G5完全Plan、backend/State lineage、残時間/費用|private Planレビューと承認記録だけ|bootstrap承認の流用、再作成以外の差分、5hまでの実施/cleanup余裕不足|Plan/input/backend/code SHA、許可action・期限|
|G7|fixture apply：未承認|G6承認、15分以内の費用、全hash一致|承認Planでfixture bucket 1＋付随設定だけ作成|想定外差分/既存資源/費用・時間閾値、部分失敗|private State/receipt、bucket設定・作成時刻、数量/費用|
|G8|IAM・lock・canary・再構築確認：未承認|G7 receipt、canary/lock方式の承認、writer停止、再作成Planの別承認、45世代/45MiB未満|T12/T13部分の固定probe、fixture cleanup→Plan→承認後再apply|想定外allow、AccessDenied以外、lock ID不一致/timeout、force unlock要求、数量80%、5h到達|許可対照・拒否分類、canary version、lock ID/412、解除後対照、再作成Plan/receipt。rawはprivate|
|G9|cleanup：未承認|writer停止、private State/証跡export、全世代inventory hashの人間確認、費用/残時間|fixture→backendの全version/marker削除、bucket不存在、作成由来の3 role削除|unknown multipart、receipt/RoleId/tag/account不一致、依存/権限不明、KMS以外が同日内に消せない|全世代inventory、削除対象/結果、NoSuchBucket/NoSuchEntityと未確認の区別、費用/残存|
|G10|KMS PendingDeletion追跡開始：未承認|2 bucket不存在、local暗号化依存解消、key ARN/type/region/tag、後日担当|key 1個だけ7日ScheduleKeyDeletion。取消/rotation/別keyなし|依存残存、key不一致、予定日不明、別key/別region|KeyId/region/KeyState/実DeletionDate/予約時刻/担当役割をprivate保存。公開はIDを伏せた予定日時・状態|
|G11|後日KMS不存在確認：未承認・別工程|G10 receipt、実DeletionDate、ユーザー本人、別のread承認|DeletionDate以降かつ＋24h以内に当該keyだけDescribeKey|時刻前、ID不一致、AccessDenied/通信失敗、別操作要求|NotFoundExceptionだけを不存在。PendingDeletion/別state/権限不明は残存又は未確認としてresource-inventory更新|

G1は課金資源を作らないため、C-1の6h実行枠を開始しない。G4の最初の課金操作前に、別途記録する開始時刻から起算する。G2/G5のPlanはreadやState書込みを伴い得るためG1承認に含めない。

## 次工程G1の最小API候補

固定コードの `preflight` が発行する候補は合計最大6 attempt、SDK/CLI retry 0（CLI max attempts 1）。エラーでも同じturnで再試行しない。AWS認証を用いるため、すべて次の別承認待ちである。

|順序/API・回数|必要権限|取得情報と判定|機密性・保存|課金可能性|
|---|---|---|---|---|
|1. STS `GetCallerIdentity` ×1|AWS仕様上、この呼出し自体に権限は不要。ただし使用する認証profileは別途承認|Account、Arn、UserId。private account IDと既存operator roleのassumed-role ARNに一致した場合だけ継続|account ID/ARN/UserIdは管理情報。rawは国内private、公開は一致/不一致と置換hashのみ|STS呼出しの直接料金は想定しない。監査・通信・組織契約の間接費Uは未確認|
|2–3. S3 `GetBucketLocation` ×2（正確なbackend/fixture候補名、`ExpectedBucketOwner`指定）|`s3:GetBucketLocation`。ただし存在しない名前の確認結果や他account所有時の応答は権限/サービス挙動に依存|各名前が`NoSuchBucket`なら未使用候補。応答成功、AccessDenied、別errorは既存又は不明として停止。bucket一覧は取らない|bucket名はaccount IDを含む管理情報。raw/nameはprivate。公開は用途別の不存在/不明、置換hash、error分類のみ|S3 request meterと監査/通信費が生じ得る。2 attemptを500円枠のAPI量へ算入し、無料扱いしない|
|4–6. IAM `GetRole` ×3（計算済みplan/apply/cleanup名）|`iam:GetRole`を当該3 role名に限定|各`NoSuchEntity`なら未使用候補。roleが返る、AccessDenied、別errorは停止。全role一覧・policy本文は取らない|role名/ARN/RoleId/信頼policy等を返し得るためrawはprivate。公開は役割別の不存在/不明と置換hashだけ|IAM呼出しの直接料金は想定しない。CloudTrail等の記録・契約費Uは未確認|

根拠：AWS公式の[GetCallerIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html)、[S3 GetBucketLocation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketLocation.html)、[IAM GetRole](https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetRole.html)。AWSはregion確認にHeadBucketを推奨しているが、固定コードは不存在を厳格に扱うGetBucketLocationを使う。HeadBucketへ変更する場合は固定コード変更としてCP2失効・再レビューとする。

### G1に含めないread候補

|候補|扱い|
|---|---|
|`iam:SimulatePrincipalPolicy` / `GetContextKeysForPrincipalPolicy`|operatorの権限情報を広く開示し、simulationはlive挙動と異なり得る。[公式制約](https://docs.aws.amazon.com/IAM/latest/APIReference/API_SimulatePrincipalPolicy.html)を踏まえ、G1の6 callsには含めない。G2前に必要なら対象Action/ARN/最大call数/保存内容を別承認|
|CloudTrail `DescribeTrails/GetEventSelectors`、Config `DescribeConfigurationRecorders/Status`、GuardDuty `ListDetectors/GetDetector`|U-accountの説明にaccount-wide設定確認が必要な場合の条件候補。trail/role/detector等の管理情報を返す。現在はAPI数・権限・保存・間接費が未承認なので実行しない。account所有者の既知回答で有限化できなければ、これら専用のread工程を先に承認するかG2を停止|
|Cost Explorer `GetCostAndUsage`、Budgets read、S3/IAM/KMSの全一覧|G1から除外。account-wideの請求/資源情報を取得し、呼出し料金や情報範囲が増える。500円のサービス側強制上限にもならない。必要なら独立承認|
|KMS `DescribeKey/ListResourceTags`|G1時点でkeyは未作成。G4後のbinding/G10/G11だけで当該作成receiptのkeyに限定|
|Terraform init/Plan/provider read|G2/G5。G1ではremote backendにも接続しない|

## G1前に追加で必要な人間承認

1. 実account ID、既存operator role ARN、AWS CLI profile、experiment IDと計算済み5名称を**private入力**としてbindする。
2. 国内本人管理PC、暗号化されたrepo外証跡dir、通信proxy/endpoint、AWS CLI版を確認する。実ID・資格・raw出力を公開しない。
3. G1の上記6 API attemptだけを、絶対開始/終了JST（提案30分以内）とともに許可する。エラー時の追加callは再承認。
4. APIによる管理metadata経路の限定例外がG1にも適用されること、S3/監査等のごく小さい未反映費を500円枠へ含めることを確認する。
5. U-accountを既知回答で有限化できるか回答する。できなければaccount-wide APIを黙って追加せず、専用read候補を別承認する。
6. G1はread-only preflightだけで、Plan、remote backend、resource作成、請求照会を許可しないと明示する。

G1がPASSしてもbootstrap Planを作る権限にはならない。G2のAPI一覧・最大attempt、必要operator権限、Uと費用見込を固定して次の承認へ戻す。
