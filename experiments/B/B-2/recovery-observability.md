# 復旧・保持/削除・監視の参考設計

未承認、全試験未実施。[構成](design.md)、[実証対応](validation-plan.md)。SLAや典型的failover秒数をE2E保証へ読み替えない。

## 障害と全依存（REQ-09/10/11/13）

RTOの設計時間配分は影響発生→検知120秒→切替/起動600秒→接続/再試行/整合確認480秒→実時間300秒安定確認→予備300秒＝1800秒。これは実測根拠のない配分であり上限保証ではない。t0は最初の影響時刻（注入時刻だけで代用しない）、t1は主要機能が300秒連続安定を完了した時刻。t1−t0≦1800秒が合否。

|障害|検知・回復候補|依存・失敗時の限界|
|---|---|---|
|Web process停止|15秒間隔health、2回失敗で除外候補、ECS restart。残taskへroute|health閾値はC検証。HTTPだけ正常でDB/auth不通を見逃さない。全target unhealthy時のALB挙動も試験|
|task/実行基盤停止|ECS replacement、既存正常image digest、readiness後登録|ECR/S3 image layer、execution role、Secrets/KMS、DNS、ECS API、quota、AZ capacityが必要。CIがなくても再起動できること|
|DB障害|RDS同期standbyへ自動failover、writer endpoint再解決、pool破棄→再接続|DNS stale/長時間transactionをタイムアウト、未確定transactionのみ冪等retry。成功応答済み更新の欠損を検査|
|単一AZ|残AZ app/ALBで継続、DBが失われた側ならfailover、残AZへ補充|残1task能力も再補充capacityも未確認。AZ除外/killで本当のAZ全停止を完全模擬したとはしない|
|認証/session|writer HAに追従、既存sessionと新規loginを毎回確認|hash CPU、clock、失効、MFA鍵、ライブラリ欠陥は別障害。メールpassword reset停止を既存login成功で隠さない|
|DNS/ACM/WAF|正常設定維持・期限検知・限定した既知正常config rollback|誤DNS、期限切れ、provider全体障害の自動復旧上限なし。これで主要操作を阻害した時間はSLOへ算入|
|KMS/Secrets/registry|正常imageと鍵/secretを国内別地域にも用意、rotation中は互換期間|稼働taskのキャッシュは新規task復旧保証でない。権限誤削除/両地域鍵喪失は夜間手動なしで解けない|
|S3/画像|regional冗長、短いtimeoutと限定retry。静的障害を検知|app streamingの遅延・memory圧迫が主要APIへ波及し得る。画像障害で正常終了できない主要操作は障害算入|
|mail worker/SES|lease回収、再送/滞留監視。DB内outboxを保持|メールは別SLI、exactly-onceなし。削除済み宛先への復元後再送を防ぐ|
|監視基盤|地域相互のheartbeat/期限欠測alarm、scheduler/DLQ/runtime監視|2地点ともAWSなのでprovider共通故障は盲点。別provider監視は所在地/費用を再確認し追加候補、現構成で独立性を保証しない|

DBは同期複製で確定データを守る設計だがRPO実績ではない。試験では単調連番/commit時刻を付けた合成更新と成功応答の記録を別観測点に保持し、復旧後の最新確定時刻との差≦300秒、成功済み行の欠損/重複/関連整合を検査する。古いbackupから戻す処理を単一AZの正常failover代替にしない。

## 論理破損・正常更新救済（REQ-11/23）

復旧開始判断から4時間が暫定目標。発見までの時間と夜間の判断待ちは別記し、4時間に含まれないことを理由に月間SLOから停止を除外しない。

1. 判断時刻を記録し、書込みを止め、汚染現行DBを隔離。直前の合成/非PII監査連番を保存（配分15分）。
2. 汚染直前の復元点・backup manifest/schema/imageを選び、private隔離DBへPITR。送信workerと外部公開は停止（60分）。
3. 現行側に残る正常更新をoperation ID/row version/actor権限/変更履歴から抽出し、汚染操作を除外した再適用一覧を作る（60分）。WALやログを無条件再生すると破損も再生するため禁止。application change historyはDB内のPII管理対象、最大7日・退会時削除で、一般ログとは分離する。容量は初期20GBに含められるか未確認。
4. 独立削除台帳を適用し、退会user/profile/favorite/session/outbox/画像派生物/抑止宛先を再削除。台帳欠落・copy遅延・原期限超過のbackupは公開不可（30分）。
5. row件数/参照整合/最新確定更新/本人認可/全session無効化/メール再送防止を確認、人間が救済不能一覧を確認後切替、300秒安定確認（45分）。残り30分は予備。

削除・上書きされた正常更新が現行DB/履歴に残らなければ完全救済不能。救済不明を黙って破棄せず損失範囲・最新復元点を明記して利用再開判断へ。4時間を達成できなければ未達を記録する。7日より古い発見を復元できるという承認はない。

## 保持・退会削除・再削除（REQ-07/08/16）

7日を最低PITR窓とする条件付き共通案。8日native backup、日次dump2世代、画像非current7日、手動/最終snapshotも最大8日を候補にする。法定最低保持や7日超の業務必要性を確認できたという意味ではない。B-1の30日案に戻す場合は下記台帳の時間整合を再設計する。

|対象|期限と実施|確認/失敗時|
|---|---|---|
|稼働DB・session・outbox・変更履歴|退会時session即失効。削除transaction/後続jobを24時間以内完了目標、正式上限は30日|毎日owner関連ゼロを確認。失敗を期限付き追跡し再送。退会日時起算で上限を延長しない|
|native backup/WAL|AWS/Azure8日、GCP logs7日＋8日次世代。停止時間による保持延長を監視|AWS停止中時間はbackup保持計算から除かれる点に注意。本番長期停止時は年齢別削除/保持設定解除の別判断。全案generation数だけで実日数保証しない|
|dump/restore用copy/隔離DB|dump直近2世代、最大8日。copy元snapshot時刻と期限を継承、restore cloneは24h作業目標|再copy/再snapshotで期限をリセットしない。隔離環境の新backupを無効化または原期限以内へ制限|
|画像全version/DRcopy|noncurrent7日、元version削除期限を宛先へ伝搬。現行画像は業務データ、退会関連なら30日以内|delete markerだけでは旧版が残る。version ID指定削除、multipart残片、soft delete相当も棚卸し|
|manual/final snapshot/停止DB|無期限作成を禁止。作成時origin/expiry必須、最大8日|retained backupと復元テストcopyも同じcollectorで検出。35日超を許すlockは設定しない|
|削除台帳|独立国内store、opaque user ID＋退会時刻＋削除完了watermarkのみ。PIIとみなし退会28日以内に全稼働copyから消去|台帳は匿名データと断定しない。t退会＋14日までに旧データを含む全復元元を消去確認。未確認ならその復元元からの公開を禁止。28日到来時に台帳を延命して解決しない|
|台帳のbackup/複製|大阪の独立copyは期限を継承し、新旧版を残さない。DB復元対象とは別。backupを作る場合も元退会＋28日以内で削除|古い台帳を通常DB backupから復活させない。台帳が失われたらrestore失敗として公開停止。個別対応が30日を超えれば要件未達|
|SES/配信イベント|退会時account suppression宛先を明示削除。event raw保存は行わず必要状態を短期outboxへ|provider内部metadata/再試行キュー/受信側copyの期限と所在地は未確認。メール抑止解除後に再送されないようDB送信資格も削除|
|log/trace/監査|PIIを抑え30日、実PII混入時は該当store/全versionを30日以内削除|CloudTrail等mandatory metadataやraw errorへの混入を未確認として残す。法令適合完了としない|

毎日全region/全管理accountの実験対象backup・snapshot・object version・隔離DB・retained backupを収集。30日で期限接近アラート、35日到達は重大違反。ただしこの案の通常削除期限8日/台帳28日が先であり35日まで放置しない。Lifecycleは非同期なので、明示削除と存在確認を併用する。物理媒体上消去やprovider内部copyの保証は公開資料/契約確認のU02に残す。

台帳再削除は①退会commit＋outbox②独立台帳への冪等反映③台帳watermark検査④restore後に最新台帳適用⑤公開、の順。東京喪失時に未反映退会があり得るため、最新性を証明できない大阪台帳だけで公開しない。地域DRのRPOを小さく見せない。キー失効/crypto-shredだけでデータ削除完了としない。

## 国内地域停止（REQ-24）

大阪の2世代dump・画像・正常image/schema/依存lock・state保管・regional key/secret・削除台帳から、人間判断後に国内cold restore。復元アカウント権限、DNS切替、証明書取得、SES identity/送信quotaを含む資材台帳をCで検証する。東京KMSを使えなければ復号できないcopyはDR資材として不合格。

日次dumpが成功していても地域RPO目安は24h＋失敗/転送遅延、台帳未反映なら利用再開保留。30分/5分は対象外。時間保証なし、国内capacity/管理API全体停止は復旧不能の可能性。平常費は[cost](cost.md)に含み、復旧時の並行稼働は別額。海外regionへの退避は採用しない。

## SLI・欠測・安定確認（REQ-06/09）

外形flowはlogin→一覧→詳細→profile参照→profile更新→本人再参照→favorite追加→favorite参照→favorite削除→logoutの10step。stepごとにHTTPだけでなく内容/権限/更新反映を検査。別のnegative auth/session失効検査はCと日次運用に分ける。synthetic accountは専用、実PIIなし、生成favorite等を毎flow消去する。

2国内地点各毎分1flow、各10秒は費用仮定。操作別latency/errorを記録し、probe母数だけでは本番API p95を推定しない。実APIはendpoint template別duration histogramと5xx/timeout、rate-limit拒否を別計測。server error<1%の分母は対象API要求、業務上正常な4xxと過負荷429を別開示し、利用不能をSLOから隠さない。低sampleではp95を未確定表示する。

外形の各時間bucketは両地点で全主要step成功の場合のみgood。片地点障害はbadとcoverageを並記し、利用者固有端末/回線だけ除外。欠測はunknownとしてgoodに算入しない。暦月総時間に対するgood時間、bad時間、unknown時間、観測coverageを併記し、99.9%判定はunknownがあれば保証しない。30日月の停止許容は43.2分、31日月44.64分。計画停止と全依存停止を含む。

安定確認は単調clockで300秒間、全step・必要APIが継続正常、少なくともt=0,60,120,180,240,300の6時刻で両地点成功。1回でも失敗/欠測なら開始時刻をreset。5回成功を5分と数えない。毎分samplingの間の障害は見落とし得るため、Cでは高頻度の別観測を重ねて空白を証跡化する。

追加30seriesは10step×2地点の成功20、flow duration2、heartbeat2、coverage2、stable window2、mail滞留1、削除期限残1。追加alarm20はstep/flow/heartbeat/coverage/retentionと復旧判断用に配分する候補、具体metric dimensionで増える場合Uへ。元の10series/10alarmは基盤CPU/DB/backup等。histogramはログ集計中心とし、全bucketをcustom metricで発行すると系列費用が増えるためC前精算。

ログ10GB/月はapp4GB・DB1GB・監査2GB・probe2GB・削除/backup1GBの上限計画。traceは業務API1%=283,500/月、保持30日。超過時に重要監査を黙って捨てず費用/量を調整する。管理更新失敗、outbox age15分超/24h超、bounce増、非本番の意図せぬ起動も別通知。監視自身が正常という外部独立証明は現2地点構成では得られない。
