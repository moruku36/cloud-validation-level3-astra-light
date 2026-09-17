# Cで必要な実証項目（計画のみ）

**LC1限定補完**：本表のT01〜T16と元の合否は保持し、末尾の「LC1予定証跡差分」を追加。要件を変えず、未実施のまま。新旧設計は[4群対応](limited-completion/README.md)で識別する。

すべて未実施。合格条件は将来の判定方法で、実証済みという意味ではない。B-3で詳細工程/予算/cleanup計画とB詳細レポートを保存し、C-0で実験上限・期限・操作許可を決定する。

|要件ID|設計判断|試験/確認|合否条件|必要な証跡|
|---|---|---|---|---|
|REQ-01|3社同条件、AWSは参考|B-3文書レビュー|AのAWS指定をBの必須制約にしていない|比較条件/公式価格/判断差分|
|REQ-02|writer commit後応答・次readもwriter|T01：profile/favorite更新直後の別接続read、同時更新、owner改ざん、失効session|本人の次read反映、他人データ不可、logout-all/退会後旧session拒否。成功応答済み更新欠損なし|合成ID・要求順序・commit番号・レスポンス（秘密除外）|
|REQ-03|private画像/SQL outbox|T02：画像迂回・type/size、worker停止/SES timeout/重複受理/bounce|直接object取得不可、許可画像のみ、滞留検知・再送、曖昧送信/重複を可視化。exactly-once保証なし|送信event連番・attempt/状態・滞留timeline|
|REQ-04|登録とMAUを分離|T03：1万/100万合成登録データの容量分析|登録だけでRPS100倍にしない、index/auth容量を測定|row/index/backupサイズと条件表|
|REQ-05|10/100RPS・500人を別表現|T04：通常10RPS、100RPS15分、read/write9:1＋静的、500人think-time|要求rate/配分/時間が設定どおり、load generatorが律速でない|時系列RPS・mix・同時利用・静的転送|
|REQ-06|API別p95/error|T04：通常/peakと片AZ残容量に同じ負荷|各主要API p95≦500ms、server error<1%、429/timeoutも別開示、メール配信完了除外|入口側histogram/母数/5xx・timeout・試験時間|
|REQ-07|20GB/画像100GB・期限管理|T05：全owner削除、snapshot/version/clone棚卸し、復元後再削除|退会30日以内稼働系削除、全backup35日以内、再公開前再削除|退会/消去時刻、全世代inventory、再削除結果|
|REQ-08|国内保存/経路台帳|T06：設定export・契約/公式仕様照合、mail/log/control-planeも分類|全本番/backup国内保存を根拠付き確認。未確認は不合格/保留、法令適合宣言なし|データフロー/region/契約範囲、受信者側判断|
|REQ-09|入口から全主要flow・unknown別記|T07：月間外形計測、計画停止・依存故障・欠測注入|暦月99.9%以上、unknownで達成主張不可。短期試験で月間合格にしない|月間good/bad/unknown/coverageと除外根拠|
|REQ-10|無人復旧/1800秒|T08：process/task/DB/片AZ、ECR/KMS/Secrets/DNS接続障害も組合せ|影響発生から復旧後実時間300秒安定終了まで≦1800秒、人的操作なし|t0/t1、health/起動/pool/6時刻以上の主要step結果|
|REQ-11|確定dataを連番追跡|T08：更新中障害・再接続・冪等retry|障害時刻−復旧した最新確定data時刻≦300秒、欠損/重複/関連整合を開示|別観測点の成功応答台帳と復旧DB比較|
|REQ-12|83,248円＋U、容量未確定|T09：必要容量の実測→月額換算、全meter精算|初期本番＋非本番＋全依存税込10万円以下、無料枠/割引に依存なし|region/SKU/数量/請求meter見積、U残と感度|
|REQ-13|夜間は自動復旧のみ|T08/T10：当番不在演習、通知のみに制限|対象障害RTOが夜間手動なしで成立。不能範囲を隠さない|自動action履歴/人間介入欄/時間|
|REQ-14|managed基盤、auth/probe分担|T10：更新/障害手順を担当者が実行|専任1名へ過度集中せず担当/副担当と実工数が明確|担当承認・演習所要時間、習得/未完了事項|
|REQ-15|1000RPSと100万人を別計画|T11：将来負荷・データ成長試験|別の前提/必要容量/費用を提示、初期予算を流用しない|負荷/登録/MAU/PV別シナリオと増強判断|
|REQ-16|SG/IAM/TLS/ログ抑制|T12：owner/RBAC/secret権限否定試験、CA不正、PII混入テスト|不正権限拒否、DB相手認証成功、不正CA拒否、PII/tokenをログへ残さない|redacted policy/拒否結果/合成PII検索・保持検証|
|REQ-17|SQL/container/2AZ/WAF/CDNなし|B-3設計比較、T04/T08|各採否・代替・見直し条件があり、台数で性能を断定しない|selection/design、計測と残課題|
|REQ-18|IaC/OIDC/承認/互換rollback|T13：空環境から再構築、競合state lock、旧imageへrollback、schema互換|手作業依存明示、秘密非公開、無承認apply不可、更新整合維持|検査/plan承認記録、国内state保管、rollback結果|
|REQ-19|採点をB-3へ分離|B-3で正式採点|原初回commitと修正後を別採点、人間欄空欄維持|採点表・根拠・人間承認（別）|
|REQ-20|公開文書のみ、初回履歴保存|B-2文書検査/remote照合|必要成果物・リンク・head/base/commit一致、秘密なし|PR/Issue/remote blob SHAとrun記録|
|REQ-21|今回B-2のみという新指示を適用|B-2操作記録|クラウド操作/IaC/app/CI実装実行/merge/B-3/Cなし|run/handoff/resource-inventory|
|REQ-22|C-0承認、実験資源限定cleanup|T14：期限/停止ではなく削除、残存棚卸し、再構築|承認費用/期限内、disk/IP/LB/backup/log等の残存を追跡。削除失敗を完了にしない|前後inventory、cost、タグ/期限/削除結果|
|REQ-23|隔離PITR＋正常更新救済|T15：誤削除後の正常書込み・不明破損・再削除・台帳欠落|判断から4h暫定目標、救済不能data明示、台帳不整合なら公開不可|復元point/選別理由/損失一覧/再開承認・300秒結果|
|REQ-24|大阪cold restore|T16：東京KMS/registry不使用で国内復元|資材/鍵/台帳が使え方針/費用/限界を検証。30分/5分を判定基準に流用しない|manifest/hash/schema/image/keyアクセス/実時間/費用|

## 追加の失敗注入と証明限界

- T05は期限を短くした機能試験と実時間35日境界検証を区別。clock変更や短期試験ではprovider内部消去/全保持期間は証明できない。台帳28日期限後に古いsnapshotを持ち込む試験、cloneからの再backupによる期限延長も検査する。
- T07はscheduler停止・probe権限失効・region欠測・通知障害・誤検知を含め、unknownがgoodへ入らないことを確認。300秒確認中の1回欠測でresetする。共通AWS全停止時の盲点は低コスト試験で解消できない。
- T08のtask停止は実AZ全停止と別の証跡にする。基盤provider内部故障や容量不足を完全再現できなければ未検証範囲を残す。安定時の1回試験だけで夜間全依存RTOを保証しない。
- T09の短期請求ではmonthly minimum、継続CPU credit、31日月、長期backup増加を網羅しない。月額換算式と未精算差を残す。
- T12の技術試験では法令適合/受信者メール保存国/事業者内部metadata所在は証明できない。契約/人間判断が必要。
- T15は汚染範囲を特定できない破損、履歴ごと消去された正常更新の救済を保証しない。不可逆損失の受容は人間判断。

C詳細工程別費用、試験順、cleanupコマンド/スクリプトは今回作成しない。B-3で計画、C-0で予算・期限・操作承認を確定する。本番月額上限を実験予算に転用しない。

## LC1予定証跡差分（試験未実施、既存Tを再利用）

|要件→群/判断|既存T/C工程|追加するケース/合否・予定証跡|
|---|---|---|
|REQ-02/03/16→G2 専用画像取込|T01/T02/T12、C-2|通常app write/未承認batch/引数override/画像すり替え/偽装/過大decodeを拒否。監査失敗時は公開不可、旧content version維持。redacted role、batch/hash/version、拒否理由、raw24h消去を記録|
|REQ-07/16/23→G1 原期限/台帳/floor|T05/T14/T15、C-5、各工程cleanup|clone再backupによる期限リセット不可、台帳欠番/floor欠落は公開不可。元/先全version/multipart/PENDING/FAILED/遅着を一覧し明示消去。退会＋14/28は条件案、30/35を維持。短縮TTLと実時間証拠を分離|
|REQ-11/23/24→G1 救済/再公開|T15/T16、C-5/6|正常/汚染/競合/履歴欠落を分離、損失不明の自動公開不可。復元point/floor/連続台帳/選別根拠/損失と人間判断、20GB相当の4h暫定/300秒安定を記録。東京不使用の鍵/image/台帳利用証拠|
|REQ-08/16/18→G2/G4 国内経路|T06/T12/T13、C-1のState/監査、C-2/9|国内保存設定＋サービス内部metadataの契約/公式範囲を照合。DNS query監査欠落を明示。sink成功をSES/受信側保存適合にしない。State/Planは国内、PRにはマスク要約|
|REQ-04/05/06/15/17→G3 容量仮説|T03/T04/T11、C-3/7|API別histogram/母数/実RPSとq、pool `25n+10`＋import予約、row/index/履歴/WAL/backup容量。追加taskだけでDB律速解消としない。1M登録と1000RPSは独立|
|REQ-09/10/11/13→G3 依存回復|T07/T08/T10、C-2/4|依存表の1件ごと復旧主体/権限/回復不能を記録。注入解除による自然回復と自動置換を区別。t0〜300秒安定終了≤1800秒、RPO≤300秒、欠測reset。手動介入/真のAZ未試験/共通盲点を開示|
|REQ-13/14/18→G2 保守責任|T10/T13、C-10（authを含む場合C-2前に担当/版固定）|主副の担当受入、休暇時手順、月次patch/CA/旧digest rollbackの実所要時間と未完了を記録。架空の担当/工数で合格にしない|
|REQ-12/22→G4 費用|T09/T14、C各課金工程、C-8分析|LC-C01〜04の数量とLC-U01〜05の全meter、既存額との重複/差分、削除後見込/反映遅延を追跡。短期請求を月額10万円適合へ転記しない|
|REQ-16/18/22→G4 再構築/cleanup|T12/T13/T14、C-1/9/10|国内S3 lock競合、別環境/任意PassRole/無承認apply拒否、互換schema rollback。backend最後の削除、鍵PendingDeletionは残存、API拒否を不存在としない。前後inventory/期限/後日確認担当を記録|

将来の限定C-1で全T12/T13を終えたとはしない。authや本番相当性能を省く範囲を承認し、残るTは未実施のまま。既存C-2→3→4→5→6等の依存は変更せず、単独実験へ切り出す場合は別の前提/費用/例外承認が必要。
