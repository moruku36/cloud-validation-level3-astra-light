# Issue #4 論点ごとの判断・根拠・未検証・方法

|論点|現時点の判断/根拠|未検証/限界|検証方法（Cで許可後）|
|---|---|---|---|
|夜間RTO/RPO|2AZ常時task＋RDS同期standby、自動切替。S09〜12|片AZ容量、長transaction、DNS/接続、Cognito内部障害。全障害30/5は未証明|100RPS下task停止、DB failover、可能なAZ注入を区別。影響開始〜5分安定終了≤30分、確定marker欠損≤5分|
|国内保存/税込10万円|東京正本・大阪copy、CFなし、regional認証/メール。S01〜08,S13〜18|受信者メール地域、細目予算枠。20%余裕で残782円、為替165なら超過|各保存転送先、地域設定・契約確認、料金表再積算、実使用量から予測。全コピー国内を必要とする場合はメールを未達として調整|
|PVと負荷/使用量|28.35百万API/月の保守仮定、100万PVとは別。static約1百万/200GB|通常10RPSの時間率、メール/log/APIサイズ/非本番時間|トラフィック計画と要求数・bytes・mail/log観測。2KB→20KB感度をcost.mdに保存|
|SLI/性能測定|機能別毎分probe、停止和集合/暦月、通常60分/peak15分、p95<条件|probe1分解像度、2秒timeout仮定、欠測は未判定。月次SLO実績なし|外部E2E、API別p95≤500ms/5xx<1%、timeout/throttle含む。月次は継続観測が必要|
|本人参照/退会再削除|writer read・commit成功後応答・削除台帳|cache設定誤り/台帳巻戻り/認証削除漏れ|更新直後別task参照、障害時retry/重複、退会後backup restore→非公開で再削除確認|
|論理破損/地域停止|PITR隔離復元・選択救済、東京→大阪日次copy|4h未実測、認証パスワード復旧不能、24h＋copy遅延の損失|合成破損復元・正常更新救済差分、コピー失敗、IaC cold再構築、受入不能は損失明記|
|将来1000RPS/100万人|固定閾値でなくCPU/接続/credit/latency/費用を見て増強|単task性能、DB拡張、100万人のMAU/要求比不明|1000RPS独立試験、MAU幅で認証費算定。初期10万円を成長上限にしない|

Issue #4は設計判断記録済みとして更新するが未検証項目が残るためOPEN維持。A-3では重点レビュー、Cで実測。詳細はdesign.md / recovery-operations.md / cost.md / sources.md。初期service SLAのcredit条件はアプリSLOやRTOの保証ではない。サービスSLA数値の掛算で99.9%達成とは判定しない。
