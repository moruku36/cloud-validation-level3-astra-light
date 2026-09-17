# G4：費用U・State・隔離・cleanup・残存例外

改版LC1、設計のみ。根拠：C-0 [第4群](../../../C/C-0/decision.md)、M09/M11/M13、REQ-12/16/18/20/22、B-3 F01/F10。[cost](../cost.md)とJSONのLC1差分、[試験追跡](../validation-plan.md)と併読。以下の作成/停止/削除は将来の手順案であり今回の操作許可ではない。

## 隔離とState/承認境界

対象は専用AWS実験account/東京VPC、国内実行環境、実験ID・所有役割・expires_atタグ、合成データのみ。大阪は承認された監視/復旧資材/鍵だけ。prod/devとのpeering・共有DB・共有State・既存DNS書換えは禁止。account/実region・resource ARN・開始/終了JST・連絡先は未回答で、公開資料には架空値を実値として埋めない。

|主体/保存先|具体設計|
|---|---|
|国内実行環境|cloud資格/Plan/Stateを扱う操作は承認された国内実行環境のみ。GitHubへマスク要約とcommitを返す。設置場所/運営/metadata経路は実行前回答が必要、無料の既存環境ありとはしない|
|backend|東京private versioned S3＋専用KMS、環境ごとbucket/keyを分離。S3 native lock `use_lockfile=true`を設計方式とする。DynamoDBを新規前提にしない。対応Terraform/provider版・lockファイル・配布checksumは実装準備で固定|
|plan role|対象account/regionのread主体。state keyのGet、lockを伴うplanでは専用`.tflock`へのGet/Put/Delete。resource変更不可。Planには機密が含まれるためPRに添付しない|
|apply role|人間のPlan承認（SHA/対象/差分/期限）後に短命資格を取得。stateのGet/Putとlock専用Get/Put/Delete。通常applyにstate本体Delete権限は不要。別環境prefixと任意PassRoleを拒否|
|bootstrap/cleanup管理|backend自身を業務stackと別manifest/stateで管理。通常destroyはbackend/鍵を消さない。最後のcleanup管理roleが前後inventoryと非機密鍵台帳を確保した後にstate全世代/lock/bucketを消す|

S3 lock/権限方式は[HashiCorp公式](https://developer.hashicorp.com/terraform/language/backend/s3)を2026-09-10確認。lock残存は稼働所有者/leaseと実行状態を照合し、競合中に強制解除しない。source/target schemaの互換期間はexpand→旧新image両対応→検証後contract。破壊的schema変更をapp rollbackと同時実行しない。T13で空環境再構築/lock競合/旧digest互換を確認するまで実装済みとしない。

## 1工程の実行封筒（未承認案）

C-1候補は既存L6h、送信0通/負荷・故障なし。T12/T13/T14の対象部分のみ。開始/終了/cleanup期限と予算上限B/全体上限/U枠/主副担当を確定してから開始可能。期限直前まで作業せず、終了前60分をcleanup枠とする案。時間不足時は実行に入らない。C-2以降の本番相当/保持/送信/故障は既存計画の別工程・別承認を維持する。

費用監視は15分ごとにquantity×elapsedと未反映見込を更新、利用可能な請求/通知値も照合する案。`実績+未反映+cleanup見込+残存見込 >= 承認B`、又は既存70%B案到達、又は終了−60分の最も早い時点で新規作成/拡張を停止。閾値の数値は未承認。課金通知を厳密な上限とせず、削除遅延/DNS非日割り/CPU credit/延長で超過し得る。予算不足なら保護機能を落とさず中断・再承認。

## cleanup順序と権限・完了証拠

|順序|手順/限定権限|確認/失敗時|
|---|---|---|
|0 開始前|read inventoryを全許可region/サービスで取得、実験manifestと既存を区別。対象単位で作成/変更/削除の承認を照合|tagだけで削除しない。既存/由来不明は作業対象外、相違があれば開始停止|
|1 安全停止|負荷generator/SES送信経路を止め、注入を解除（該当工程だけ）、scheduler/worker/自動scaleの再作成を停止。復旧用read/削除資格は残す|解除成功と予約消去を記録。失敗なら再試験しない、当日の主副へ連絡。今回連絡/送信を実施しない|
|2 証跡/State保全|合成試験結果・費用/資材一覧をマスク、国内保存先へ。依存資源がある間は必要なsecret/key/Stateを保持|公開GitHubは非機密要約のみ。State/Plan/PIIを証跡として公開しない|
|3 DB/復元資材|隔離clone→実験DB→retained automated backup/manual/final snapshotを確認して削除。C短期合成DBは最終snapshot不要の案、追加保存は別承認。RDS deletion protection解除は対象DBに限定|削除要求受付で完了にしない。pending/failedと費用見込を台帳化。G1の原期限を子資材にも適用|
|4 object/画像/資材|raw/import job/dump・元/先全version/delete marker/multipartをG1順序で消去。ECR imageと承認済みsecret/log/traceを個別削除|遅着複製/自動再生成がないか再取得。Secrets等に待機が残る場合は例外未承認なら作成前に止める|
|5 入口/基盤|ECS service/task、ALB/listener/target/WAF関連、専用DNS/証明書、専用SG/network、IP/disk/endpoint/NATがある場合のみ依存順削除|既存共有zone/cert/networkを消さない。C-9以外へ未選定NATを追加しない。止めたtaskだけで費用ゼロにしない|
|6 State/keys以外の終了確認|全account対象region/manifestを再照合、対象外既存の不変を確認。ログ等必要な診断対象が残る場合は終了前に理由/期限/費用を人間判断へ|期限超過/権限喪失はcleanup失敗。復旧用最小情報を先に消さず、未承認保持を成功と報告しない|
|7 backend/最後の鍵|上記資源が不存在となったらStateの全世代/lock/復旧copyを消去。鍵ごとの非秘密ID/region/予定削除日時を保全し、残存鍵だけScheduleKeyDeletion|暗号化Stateを消す前に依存削除確認。鍵PendingDeletionは残存。backendを依存の先頭でdestroyしない|

削除のActionは対象manifestのARNへ限定し、IAM/key操作は通常app/restore権限外。削除失敗後の対応は再読取り→依存/権限/保護設定の理由記録→承認済み修復範囲なら再試行→範囲外/期限危険なら人間判断。勝手な権限拡大や既存資源削除は禁止。

## 即時削除できない資源の例外票に渡す項目

|対象|残存案/期限/費用|後日確認・例外不承認時|
|---|---|---|
|KMS|既存案の7日待機＋予定削除から最大24h後までの確認。各鍵に依存ゼロ確認時刻、Schedule時刻、region、実期限JST、所有/副担当を記録。待機は残存、取消時費用もU|期限後のDescribe相当で不存在と権限拒否を区別。権限不足は未確認。後日確認を別工程依頼し、実行予約を今回作らない。例外未承認なら鍵作成不可|
|Secrets等|削除待機を使う場合のサービス別期限/量/料金/取消条件をE10へ追加。今回はサービスの待機設定を確定せず、未承認例外で作成しない|復旧不要として即時削除を選ぶ場合も対象と不可逆操作を事前承認。KMS例外に便乗して保持しない|
|State/診断情報|同日消去が原則。削除失敗調査に必要なら最小の非公開暗号化情報、理由/保持終了/主副/費用を記録|資源残存中に復旧情報を破棄しない。一方、無期限の保持承認にはならず中断/超過を報告する|

KMSの既存仕様根拠は[B-3限定修正](../../B-3/revised-design.md)。鍵数量はLC1で実数未確定、現在の実資源ではない。KMS待機分を他の残存DB/storage無料化の根拠にしない。

## G4の完了境界

費用は既知の既存単価×数量の条件付き差分とUを分離（[cost/JSON](../cost.md)）。全体/工程予算・U枠・account/実ARN/実日時はH待ち。State方式/権限分離/削除順序/失敗分岐はD補完。対象への具体的binding・Plan・版固定は限定実験の実装準備で必須、実測待ちという理由ではない。T09/T12/T13/T14で量/否定/再構築/残存を確認し、短期費用で本番月額適合を証明しない。
