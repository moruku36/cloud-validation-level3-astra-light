# 判断に使用した公式出典

確認日：2026-09-09。仕様は公式資料、価格は地域料金表を優先。検索で混在した第三者サイトは根拠に使用していない。単価は採用時点の見積資料であり将来固定価格ではない。

|ID|公式URL|確認した事実・用途|
|---|---|---|
|S01|https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/ap-northeast-1/index.json|PostgreSQL t4g.medium Multi-AZ0.202USD/h、small Single-AZ0.05、gp3 Multi-AZ0.276/GB月。SKU/発行日はofficial-rates.json|
|S02|https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/ap-northeast-1/index.json|ARM Fargate0.04045/vCPU-h・0.00442/GB-h。公式抽出保存|
|S03|https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSELB/current/ap-northeast-1/index.json|ALB0.0243/h、LCU0.008/h。Outposts/予約LCUを見積対象にしない|
|S04|https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-northeast-1/index.json|Standard0.025/GB月、PUT0.0047/1000、GET0.0037/10000。s3-rates.json|
|S05|https://aws.amazon.com/cognito/pricing/|Lite最初の有料帯0.0055/MAU。比較は無料枠を控除せず1万人全額で算定|
|S06|https://aws.amazon.com/waf/pricing/|ACL5/月、rule1/月、0.60/百万要求。追加機能別料金|
|S07|https://aws.amazon.com/vpc/pricing/|public IPv4 0.005/address-hour。task/ALB数を含める|
|S08|https://aws.amazon.com/ses/pricing/|送信・データ等の従量課金。今回2USDの予算枠、東京精密見積未完|
|S09|https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.Failover.html|自動切替、典型60〜120秒、長transactionで増大、DNS/接続再確立が必要。上限保証ではない|
|S10|https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html|別AZの同期standby。readable standbyではない|
|S11|https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-rebalancing.html|ECSのAZ再配置機能。残存容量があることとは別|
|S12|https://aws.amazon.com/about-aws/whats-new/2023/10/amazon-ecs-applications-resiliency-unpredictable-load-spikes/|unhealthy taskをhealthy replacementへ置換するECS機構|
|S13|https://docs.aws.amazon.com/cognito/latest/developerguide/data-protection.html|user pool暗号化、managed loginのCloudFront依存|
|S14|https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-email.html|東京user poolのSES送信元地域を明示可能。海外設定を避ける|
|S15|https://docs.aws.amazon.com/pdfs/cognito/latest/developerguide/cognito-dg.pdf|Regional data considerations：profileはuser pool地域、optional featuresで他地域転送あり|
|S16|https://aws.amazon.com/compliance/privacy-features/|SES等は受信先へのデータ転送が機能の一部。地域指定のみで全受信コピー国内を保証できない|
|S17|https://aws.amazon.com/cloudfront/faqs/|global edge/regional cacheを使用|
|S18|https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesEnableGeoRestriction.html|viewer地域制限。国内cache保存保証として流用しない|
|S19|https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html|PITR・snapshot。backupと同期待機切替は異なる|
|S20|https://aws.amazon.com/rds/faqs/|最大35日・LatestRestorableTimeまでの復元。時点復元だけで5分RPOを保証しない|
|S21|https://docs.aws.amazon.com/lambda/latest/dg/provisioned-concurrency.html|cold start対策のprovisioned concurrencyは追加費用|
|S22|https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html|tableの強整合とGSI結果整合を区別する比較上の論点|

S01〜04はcurlのTLS検証を維持して取得し、必要SKUのみ保存。Python urllibはローカルCA不足で失敗したためcurlへ切替、証明書検証を無効化していない。価格原本全体はwork/に置き、公開証跡は抽出単価とURL・発行日。料金表の発行日は確認日とは別。
