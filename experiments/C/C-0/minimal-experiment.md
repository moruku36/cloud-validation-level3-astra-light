# CP1：最小C-1承認案・準備判定（2026-09-11）

**判定B：人間の回答後、下記binding欄を確定すれば承認可能。全承認欄は未承認。** 今回は文書のみ。設計不合格、66／66／66点、LC1未採点、最終選定・人間採点・採用承認・C移行保留、構築開始不可を維持する。

## 固定する設計と次の1工程

起点はPR #16 head `f843183def131b1c42f2b192bdb72392f5150bad`。同SHAの以下を固定参照する（B-2原文＋B-3限定修正＋LC1＋C-0を継承）。

- `experiments/B/B-2/limited-completion/experiment-lifecycle.md`：State、IAM、cleanup、残存例外。
- `experiments/B/B-2/limited-completion/iam-operations-data.md`：国内経路・責任分離。
- `experiments/B/B-2/validation-plan.md`：既存T12/T13/T14の定義。
- `experiments/B/B-3/c-validation-plan.md`：C-1、通常ゲートと例外条件。
- `experiments/C/C-0/blockers.md`：M04/M06/M09/M10/M11/M13。
- `docs/execution-policy.md`：1工程、全体/工程予算、同日cleanup、State保全。

次の1工程案は **C-1のState・lock・IAM境界・cleanupだけの限定実装と確認**。旧LのFargate/DB/ALB一式は含めず、旧C-1全体の完了としない。AWS東京を使う理由は優先参考設計のS3/KMS方式を直接確認できるためで、最終クラウド選定ではない。

机上記述では未確認の「native lockの競合拒否」「通常操作主体の削除/他prefix拒否」「backendを残した試験用bucket再作成」「最後の全世代消去と鍵待機移行」を確認する価値がある。業務データ、DB、メール、片AZ基盤を作らずに確認できる最小の依存集合である。

### 実装・Plan・実行版の区別

今回固定するのは設計版であり、**この小範囲専用の実行コード・実行可能な固定SHAは未作成**。次工程ではbackend bootstrapとfixtureを分けたIaC、provider lock/checksum、native lock対応Terraform版、IAM境界、数量/時間監視、cleanupと証跡抑制の手順を作る。実装commit、ツール版、国内実行環境、コードから作った操作一覧を固定する。bootstrapのローカルStateも暗号化して保全する。

承認は二段階：人間が本票の入力を確定して限定工程の準備・対象操作を承認 → 実装後に**bootstrapとfixture両方の実Plan、費用差分、対象ARN、削除権限を人間が確認しapplyを承認**。前段の承認だけでapplyしない。機密Plan/Stateは公開PRへ載せず、承認版のハッシュと非機密差分を記録する。コード作成前に実Planを固定済みとはしない。

Planで資源数、サービス、region、権限、転送、保持、単価、費用枠が本票を超える、既存資源変更が混入、backend再作成順序が不明、復旧資格/国内保存が未確定なら停止・再承認。未回答bindingをコードの推測値で埋めない。

## 承認票（CP1、すべて未承認）

|ID|具体案・確定が必要な入力|承認|
|---|---|---|
|E1 目的/範囲|上記C-1部分のみ。実装・準備、承認後の小範囲確認、cleanup。C-2以降、正式再採点、本番採用、性能/復旧/負荷/故障/メールは対象外|未承認|
|E2 account/region/隔離|**要回答**：既存の専用実験AWS accountと実行principalを非公開で指定。東京 ap-northeast-1のみ。国内の既存暗号化端末/接続を使い追加従量費なしの案。所在地・保存/転送先・主副担当は要回答。新account/有料runner作成、既存業務資源利用不可。実験ID/所有/期限タグ＋明示ARN manifestで隔離|未承認|
|E3 資源/操作|新規private S3 Standard 2個（versioned backend 1、fixture 1）、東京対称KMS鍵1個（rotation/replicaなし）、専用IAM role 3個（plan/apply/cleanup、inline policyのみ）。既存承認principalがbootstrap/role管理を行う。S3設定/暗号化/限定object操作、fixture再作成、lock、全version/delete marker消去、bucket/role削除、鍵削除予約だけ。新VPC/DB/compute/DNS/SES/監視/外部サービス/追加鍵は禁止|未承認|
|E4 データ/通信|合成objectとIaC Stateだけ。単一payload≦1MiB、multipart作成禁止。累積保存全世代≦2GB、送出≦1GB。両bucket public access block、TLS、owner enforced、他account信頼なし。国内端末→AWS API/S3/KMS、実装時の公式配布取得。State/Plan/資格/生ログは国内暗号化端末だけ。GitHubは非機密文書/コード/要約のみ。メール0通、公開endpointなし|未承認|
|E5 負荷/故障|負荷試験・故障注入なし。最大2つの同一fixture Stateに対するlock競合確認のみ、強制unlockしない。拒否確認は合成対象・専用principalだけ。可用性障害を起こす試験にはしない|未承認|
|E6 時間|提案：最初の課金資源作成から最大6h、5hで新規確認を停止しcleanup開始、6hかつ当日終了前に鍵以外削除。**要回答**：実行当日に開始/5h/6h/日付境界のJST絶対時刻と担当在席を確定。実装時間はこの稼働6hに含めず、作成前に完成させる。無人延長不可|未承認|
|E7 費用|本小工程単独：税込計画枠300円＋cleanup事故予備200円＝**承認上限案500円**。通常6h概算約28円、保守的既知費約212円（全月storage/key計上、為替160円/USD、税10%仮定）。[計算](minimal-cost-model.json)。無料枠不使用。未確定U-account/U-runner/U-taxは要回答、説明不能なら課金不可。C全体12,495円＋U、本番月額10万円は流用しない|未承認|
|E8 費用停止|15分ごとに数量×時間＋未反映＋cleanup/残存見込を更新し、利用可能な請求値と比較。見込が計画300円に達する、総枠70%の350円に達する、総見込500円以上、数量80%又は5hの最も早い時点で新規操作停止。残りはcleanup専用。通知は厳密な課金上限制御ではない。反映遅延/削除失敗/為替変化で超過し得る|未承認|
|E9 cleanup|下記順序で同日削除。既存資源は変更/削除しない。失敗は新規確認停止→原因/依存/権限確認→許可済み範囲で再試行→担当判断。権限拡張/保持延長を独断で行わない。開始/各確認終了/終了時のmanifest照合と未確認を記録|未承認|
|E10 残存例外|この鍵1個だけ削除待機7日を提案。PendingDeletionは残存。削除予約中の鍵月額は無料、取消は禁止。APIが返すDeletionDateを記録し、当該日時＋24h以内に担当が不存在を確認。7日指定でも実削除に最大24hの幅があり、相対期限で済ませず実日時を確定。後日読取確認は**別工程の依頼・承認**が必要、今回は予約もしない。担当/予算/確認依頼の責任が未定なら作成不可|未承認|
|E11 中断/保全|未知資源、想定外通信/PII、Plan逸脱、lock異常、担当不在、期限/予算危険、復旧資格喪失で中断。依存が残る間は国内暗号化State/鍵/復旧情報を破棄しない。通常は依存消去後にState全copyを同日削除し、後日確認には非秘密鍵ID/region/DeletionDateだけ保持。失敗時のState例外保持は対象/期限/費用の別判断が必要、無期限保持を許可しない|未承認|
|E12 例外の効力|設計不合格/採用未承認のまま、このC-1部分だけ進める例外。実験全体＝本小工程500円とし、以降Cの予算/操作は未承認の段階分離を明示承認する。国内所在未確認のIAM/control-plane account/操作metadata経路は当該合成実験だけの例外要否を人間判断。PII/業務dataは対象外。正式REQ-08緩和や以後Cの包括許可、本番採用承認にはならない|未承認|

IAM詳細：planは指定State Get、対象bucket List、専用tflock Get/Put/Deleteと必要KMS利用のみ。applyはState Get/Put、同lock操作、fixture管理を許可しState本体Delete/別prefix/別bucket/任意PassRoleを拒否。cleanupだけ全version/marker削除と実験bucket消去・鍵予約を許可する。bootstrap principalのrole作成/削除、鍵policy管理はこのmanifestに限定し、通常roleに自己権限拡張を与えない。ロール信頼先・session期限・ARN・KMS encryption contextを実装時bindingし人間がPlanと併読する。API上region制約できないIAMのグローバル性を東京保存の証拠にしない。

## 手順・証跡・合否

|既存対応|実施する部分と成功証拠|失敗/未確認の境界|
|---|---|---|
|REQ-16 / T12、M10/M13|applyからState削除・別prefixアクセスが拒否され、許可したState更新は成功。非機密policy摘要、操作/principal別結果、時刻|予期しない許可は失敗。一般的AccessDeniedだけで正しいpolicyと断定せず許可対照を揃える。DB TLS、app RBAC、画像IAMは未確認|
|REQ-18 / T13、M13|native lockを一方が保持中、他方が書込できず、正常解放後に成功。backendを保持してfixtureのみ消去し同じコードで再作成。State整合・Plan摘要・処理順を保存|同時書込/State損傷は失敗。コード未完成/記録欠落は未確認。アプリ空環境再構築・schema rollbackの証明ではない|
|REQ-22 / T14、M06/M11|fixture→backend内State全世代/marker→bucket→鍵依存ゼロ確認/削除予約→role消去。ローカルbootstrap Stateも依存消去後削除。前後manifest/全世代一覧・鍵状態/予定日を保存|6hで鍵以外残存はcleanup失敗。鍵待機中は例外付き暫定完了、全ライフサイクル完了ではない。後日NotFoundと権限拒否/通信不能を区別。後二者は未確認|
|REQ-12 / T09の補助のみ|数量・経過時間・推計・請求反映遅延/Uを記録|本番容量/全月10万円適合の合格判定には使わない|

終了条件：上の限定確認に証拠が揃い、当日の対象外資源不変・鍵以外不存在、鍵例外と後日責任が記録されること。不合格/未確認もそのまま記録して工程を停止し、勝手に反復・範囲拡大しない。後日の鍵不存在確認まで残存欄を閉じない。

S3全世代一覧を再取得して空を確認し、multipartは作成禁止でも一覧確認する。存在したら想定外として新規作業を止め、対象実験由来が確定したuploadだけ許可cleanupする。Stateの暗号化依存を残して鍵予約しない。実験の非秘密残存台帳は後日確認完了まで国内保管、公開GitHubには実ID/生Planを載せない。

## 必要回答・保留できる判断

|今必要な外部入力|推奨選択肢（すべて未承認）|別選択の影響|
|---|---|---|
|実account/実principal/国内端末と追加費用|既存の専用実験account＋国内既存端末、追加固定/従量費なしを確認|共有業務accountは本案対象外。有料runner/必須監査課金ありなら単価×上限数量を追加し再計算。未確定のまま開始不可|
|当日実行/停止/cleanupと後日鍵確認の主副、実施可能枠|同日6hを確保し5hでcleanup、後日確認の担当と依頼責任を指定|実在名/工数は要回答。在席/6h未確保なら短縮再計算又は延期|
|費用・保持・経路・ゲートの例外|税込500円、鍵1個7日待機、metadata未知経路の限定例外、部分C-1/段階予算を個別承認|鍵残存又はmetadata例外を認めない場合は本案開始不可。鍵なしへの変更は本State設計検証の範囲変更として別設計判断|
|適用税/請求通貨/価格と組織必須サービス|税10%、USD換算≦160円の条件を確認し、必須追加料金なしを回答|条件外なら価格・U・上限を再計算し承認。通知があっても予算保証にはしない|

メール受信側国内範囲はメールを一切使わないためC-2実送信前まで保留。最低PITR/正常更新損失はDB/復元を使わないためC-5/6前まで保留。auth/probe本番保守主副・工数は当該機能を使わないためC-2/4/10前まで保留できるが、今回実験主副の指定を代替しない。推奨済み7日PITR等を業務回答へ変更しない。

成功しても、REQ-07の全copy30/35日/複製失敗、REQ-08全国内保存、性能/片AZ/全依存無人復旧、RTO/RPO、正常更新救済、月間SLO、保守体制、メール、容量込み本番費用は未証明。本番参考構成との差分はapp/DB/ネットワーク/監視/DRを全て省略し、データ≦2GB・短時間・合成のみであること。S3/KMS/State実装の当該条件だけへ結果を適用する。

## 判断の根拠と今回具体化した点

価格は2026-09-11に公式公開情報で確認。[東京S3価格表](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-northeast-1/index.json)のStandard $0.025/GB月、Tier1 $0.0047/千件、Tier2 $0.00037/千件、[東京転送価格表](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/ap-northeast-1/index.json)の送出$0.114/GB、[KMS料金](https://aws.amazon.com/kms/pricing/)の鍵$1/月・対称要求$0.03/万件を使用。無料枠は引かない。[鍵削除仕様](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html)の待機期間と実予定日時を残存管理へ反映する。REQ-20の公開文書/版照合は文書検査でありT13の実証に混ぜない。

費用確認に新しい有料Cost Explorer API巡回等を追加しない。既存閲覧手段とローカル推計を用いる案で、利用環境が追加有料計測を要求するならU-accountへ算入して再承認する。実装時はSDK再試行を含む最大API呼出数・S3が発行するKMS要求を見積もり、数量を数えられない場合はapplyしない。

従来のaccount/数量/費用未確定のL候補から、資源2bucket/1key/3role、無送信・無負荷、6h/5hcleanup、500円、1key待機例外、T12〜14の部分証跡へ絞った。未回答業務4件に依存するapp/DBを外したので、同じ未解決事項の回答待ちだけで実験を永久停止する循環はない。

通常移行は既存C計画のB合格/人間採用ゲート未達。例外なしなら正式再評価と人間採点/採用判断が先である。本案は同計画の未解決事項限定例外とC-0の範囲別判断を用い、execution-policyの全体/工程予算・同日削除に対する段階予算/鍵例外を個別承認して初めて成立する。方針本文は改変しない。

B判定の未確定箇所は上表の実account/国内環境/担当枠/課金条件であり、追加の全面設計や採点ではない。次は回答と例外承認後のこの限定C-1準備、applyは実装/Plan承認後。今回それらを実行しない。
