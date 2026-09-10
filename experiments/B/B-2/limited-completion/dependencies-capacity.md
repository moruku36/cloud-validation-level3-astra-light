# G3：全依存の回復・回復不能範囲と片AZ容量仮説

改版LC1、設計のみ。根拠：C-0 [第3群](../../../C/C-0/decision.md)、M08/M12、F06/F08、REQ-05/06/09/10/11/13/17。既存[依存表とSLI](../recovery-observability.md)・[容量案](../design.md)へ回復主体、権限、解除/停止条件を補う。製品SLA・時間配分を実績へ昇格させない。

## 依存別の判断

「自動候補」は設計された処理の実証待ち。「回復不能」は現設計の成立しない障害を示し、実験すれば自動的に解決する扱いにしない。以下の操作は将来の許可範囲案で、今は実行しない。

|依存/故障|検知→回復主体/処理と必要権限|回復不能・停止/解除|既存試験・証跡|
|---|---|---|---|
|process/task/ECS|主要flow＋readiness。ECSのservice desired count/replacement、固定image digestで再起動。execution roleのECR/secret/logとservice roleの対象cluster操作|API/quota/AZ capacity不通で補充不能。無限起動loopは新revisionを止め直前正常revisionを維持。手動台数追加で合格化しない|T08 C-4、影響時刻・service event・起動/登録・介入履歴|
|RDS/writer/pool|DB接続と主要flow失敗、managed failover→endpoint再解決→古いpool破棄。appはDMLのみ、未確定transactionだけidempotency keyで再試行|制御面障害/全DB喪失は通常failoverで回復不能。backup復元へ自動で切替えてRPOを偽らない|T08 C-4、外部成功応答台帳対DB、再接続/欠損/重複|
|単一AZ/ALB|AZ別target/flow監視、残AZの既存taskを先に使う。service配置方針2AZ、min2/max6候補|残1task処理不足・補充遅延なら容量未達。all-target-unhealthyでもapp readiness失敗時に業務成功を返さない|T04/T08 C-3/4、AZ別task数/実RPS、真のAZ停止との未再現範囲|
|ECR/image/S3 layer|新task起動eventとdigest照合。execution roleは固定repoのpull、正常digest2版を国内保管|全image欠落/東京registry不通で新taskを起動できない。大阪imageはcold DR用で通常AZ回復時間を保証しない。稼働キャッシュを新規起動保証にしない|T08/T16 C-4/6、cold pull結果・東京不使用復元|
|KMS/Secrets|decrypt/read失敗とflow。rotationの旧新互換期間を保持し、承認済みsecret versionのみの限定rollback。通常taskはread/decryptだけ|鍵削除/権限喪失/両地域API不能は自動修復しない。期限切れsecretや失効鍵を無断復活させない。新規起動不能を宣言|T08/T12 C-4、version/key参照・拒否ログ。鍵破壊でなく実験用経路拒否を候補にする|
|DNS/ACM/WAF/ALB設定|外形/証明書期限と変更eventを照合。deploy由来の直近変更だけ、署名付き正常manifestとの差分へ戻す限定controller。対象record/listener/ruleだけwrite、IAMや鍵は変更不可|期限切れ証明書やprovider DNS全障害はrollbackで解けない。不明な設定差/攻撃判定は自動上書きせず停止。別region無断切替なし|T07/T08 C-2/4、変更前後hash・同一変更のrollback1回・回復不能時間|
|認証/session|DB復旧後も新login/既存session/失効を別確認。前互換app digestへrollback。auth主副はG2|脆弱性/破損/認可不明は機能閉鎖し夜間の無人修復を約束しない。session検査省略を回復としない|T01/T08/T10/T12 C-2/4/10|
|画像S3/取込|Get timeoutとAPI遅延、bounded retry（案：要求全体の残時間内で最大2回）。取込失敗はG2の旧版参照維持|S3停止時に画像必須の主要flowが失敗すればSLO bad。空画像で正常を偽らない。rawの直接配信禁止|T02/T04/T08、画像有無別flow/接続占有|
|outbox/SES/SNS|lease期限/age/error/bounce。workerは同じevent IDで再試行、通知失敗は国内状態storeへ記録|SES/SNS全停止は配送保証不能。既存loginとは分離、通知成功を確認できなければ実験は中断。送信資格を削除された宛先は再送しない|T02/T07/T10 C-2/4、event attempt/unknown/別連絡|
|probe/Scheduler/Lambda/log|地域相互heartbeat、1周期欠測をunknown、連続2周期欠測で停止判断用alarm（仮閾値）。独立した実験実行端末も時系列を取得|同一AWS共通障害は盲点。実験端末は安全停止監視で本番の別provider監視採用ではない。通知/観測不能なら新規注入を止める|T07/T08、coverage/good/bad/unknown・API記録との差|
|backup/台帳/floor/collector|G1の連番欠番・期限残・全copy一覧。collector限定削除、restore read、公開ゲート別主体|台帳/floor欠落はrestore公開禁止。健全稼働系は継続可、復旧を阻害する場合は未達を開示|T05/T15/T16 C-5/6、原期限/拒否/残存|
|CI/State/IAM/quota|実行時cloud操作はG4の専用国内実行環境、IAM/State到達を開始前確認。CI停止でも既存serviceは継続|CI不通を業務停止と同一視しないが、新image配布/State rollback不能は操作停止。quota増申請/全IAM再建は自動回復に含めない|T10/T13/T14 C-1/10、lock/未承認拒否・権限境界|

rollback controllerは既知の自分のdeployment revisionに限り1回戻す。現在hashが予期した変更後値と違うなら他操作を上書きしない。IAM/key/データ削除はcontroller権限外。実験runnerには注入解除用の別資格を持たせ、故障対象roleと共倒れしない（未作成）。回復不能行は本番採用前に追加設計/正式な判断が必要で、今回の文書完了から消えない。

## 容量仮説・限界・費用

|変数|今回固定する仮説/計算方法|測定と判断|
|---|---|---|
|基準容量|H＝1vCPU/2GiB×2task・2AZ、RDS medium Multi-AZ/gp3 50GB、業務20GB/画像100GB。Lは機能用の別構成|H現行案が十分という結論ではない。L結果を代用しない|
|片AZ残1task|動的100RPS×15分（read/write9:1）＋静的別要求＋auth/hashを1taskで捌く仮説。通常10RPS・500人think-timeモデルも別記|APIごとp95≤500ms/error<1%、429/timeout別。不足時はq（安全処理RPS/task）を測り`片AZ必要task数=ceil(100/q)`、2AZ合計はその2倍。測定qなしで台数を確定しない|
|CPU/memory/queue|CPU60%5分、memory70%、DB接続70%、disk余30%は既存増強検討閾値。認証/画像の同時処理はDB以外も律速になる|backpressureはbounded、拒否率を隠さない。上限到達時の新規要求拒否は性能合格でない|
|DB接続|n taskでWeb20＋worker5の各pool上限、管理予約10 → `25n+10`。n=2で60、n=6で160|実max_connections/メモリ/IO余裕と比較し、接続上限を満たすnに制限。import専用接続は追加予約が必要でU/容量表へ|
|データ/履歴|業務20GBに認証/index/7日履歴が含まれると断定しない。write平均件数×86400×P×履歴bytes、index/WAL/backup/cloneを別集計|T03で1万/100万人を分離。P>7なら差分比例だけで性能を保証せず容量とrestore時間を見直す|
|scale/費用|max6は初期仮定、追加task h×既存単価＋IP/LCU/DB credit/転送を計算|2taskを増やす例とDB/ストレージ感度はcost。1000RPSはT11の独立シナリオで別予算/承認|

`ceil(100/q)`は台数候補を作るための下限計算で、DB/ALB/静的処理を共有したまま比例scaleできる保証ではない。選んだ台数で同じ負荷・DB容量・片AZ条件をT04へ戻し確認する。必要台数が承認max/予算を超えるときは無断増強せず未達として止める。

## 時間・停止条件・証明限界

RTOは影響開始t0から全主要機能の実時間300秒安定終了t1まで≤1800秒。既存120+600+480+300+300秒は設計配分のみ。t0を検知時刻へずらさず、欠測/失敗で安定windowをreset。RPOは障害時刻と復旧最新確定data時刻の差≤300秒、成功応答済み欠損/重複も別記する。

将来C-4は各依存1件ずつ、承認baselineへ戻して開始。実験用の接続拒否/停止を最大5分の注入案とし、runner側15分で解除の独立watchdogを設計する。後者は安全措置であり5分超の正常実験を許可しない。注入解除自体で回復したのか、自動置換で回復したのかを分離する。手動救済・観測不能・境界逸脱・予算/終了期限危険なら即中断、注入を解除してG4 cleanupへ。1800秒時点未安定は不合格、待ち続けて合格にしない。

実AZ全停止・全provider停止は代替障害では証明できない。月間99.9%は暦月の全主要flowを観測し計画停止も算入、短期T07はunknown判定機能だけ。G3は依存処置/回復不能の開示/容量算定式というDを補完した。実性能/時間/未知provider障害はE、回復不能範囲の本番採用判断と主副担当はH/本番課題として残る。
