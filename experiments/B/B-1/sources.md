# B-1 重要出典と未確認事項

確認日：2026-09-09（Asia/Tokyo）。公式情報のみを判断根拠に使用。価格の地域選択・SKU・数量は別に検証する。ページ取得失敗を仕様不存在と扱わない。Aの当日抽出は再取得せず継承。Vは単価/機構の根拠であり実機適合ではない。Eは仮単価・適用未確認。

## 取得/再利用した根拠

|ID|公式出典|今回得られた根拠・限界|
|---|---|---|
|A-S01〜04|[A公式出典](../../A/A-2/sources.md)、[SKU抽出](../../A/A-2/official-rates.json)、[S3抽出](../../A/A-2/s3-rates.json)|東京RDS/Fargate/ALB/S3の2026-09-09取得済み根拠を再利用。RDS待機込み0.202/h、gp3 0.276/GB月、ARM 0.04045/vCPU-h＋0.00442/GiB-h。ALB通常SKU 98ZU8QNDMR4AS8FJ、Outpostsを不採用|
|A-S06/07|[AWS WAF](https://aws.amazon.com/waf/pricing/)、[VPC](https://aws.amazon.com/vpc/pricing/)|A取得を再利用：ACL5＋rule1/月、0.60/百万、IPv4 0.005/IP-h。無料枠除外|
|A-HA|[RDS Multi-AZ](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html)、[failover](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.Failover.html)、[ECS AZ rebalancing](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-rebalancing.html)|A公式調査を再利用。同期standby、自動復旧機構、典型60〜120秒は30分上限の証明ではない|
|A-DATA|[Aの認証/保存/削除調査](../../A/A-3/revised-design.md)、[backup](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)|PITR、Lifecycle非同期、Cognito/メールの地域条件を継承。Aの42日削除台帳は採用しない|
|Z-RATE|[Microsoft Retail Prices API](https://prices.azure.com/api/retail/prices)、[API仕様](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices)、[抽出19meter](azure-rates.json)|公開APIをGET。japaneast/Consumption/USD。ACA active CPU 0.000024/s、memory0.000003/GiB-s、request0.4/M。PostgreSQL Ddsv5 0.122/vCore-h、B1MS0.026/h、storage0.138/GB月、backup0.095。WAF v2 fixed0.522/h＋CU0.0144/h。Discounted別製品を除外|
|Z-HA|[Container Apps reliability](https://learn.microsoft.com/en-us/azure/reliability/reliability-container-apps)、[運用推奨](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-container-apps)|VNet・環境作成時zone redundancy、最小2以上。一般推奨は3replicas。今回2replicasを残1台100RPS試験条件で候補化。配置/即時容量は実証なし|
|Z-DB|[PostgreSQL reliability](https://learn.microsoft.com/en-us/azure/reliability/reliability-database-postgresql)|別zone同期HA、自動切替、主待機同額課金。BurstableはHA不可。region capacityによるsame-zone代替を適合扱いしない|
|Z-WAF|[Application Gateway料金構造](https://learn.microsoft.com/en-us/azure/application-gateway/understanding-pricing)|固定＋capacity units。2instances相当20CUを仮置き。WAF処理量/容量実測なし|
|G-RUN|[Cloud Run pricing](https://cloud.google.com/run/pricing)、[zonal redundancy](https://docs.cloud.google.com/run/docs/zonal-redundancy)、[autoscaling](https://docs.cloud.google.com/run/docs/about-instance-autoscaling)|東京/大阪Tier1、instance課金CPU0.000018/s、RAM0.000002/GiB-s。ゾーン分散はmanaged。min2を2AZ各1予約と誤認しない|
|G-SQL|[Cloud SQL pricing](https://cloud.google.com/sql/pricing)、[machine series](https://docs.cloud.google.com/sql/docs/postgres/machine-series-overview)|Web取得が複数回失敗、公開HTML直接GETは成功。デフォルトIowa Plus N2 HA CPU0.1074/h・memory0.0182/GiB-hを確認。東京選択のSKU照合は未完。東京係数1.30を仮定し0.1396/0.0237へ丸めたE値。N2最小候補2vCPU/16GBは公式確認。東京への対応価格を確認済みとは主張しない|
|G-HA|[Cloud SQL HA](https://docs.cloud.google.com/sql/docs/postgres/high-availability)|切替後接続再確立は約60秒の説明。E2E上限保証ではない。同期冗長とPITRを分離|
|G-BACKUP|[backup options](https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/backup-options)|Enterprise PITR logs1〜7日、Plus1〜35日。backup世代は別設定、手動backup無期限に注意。30日PITR共通仮定を維持する代表案はPlus、backup31世代候補。国内location指定が必要|
|G-ARMOR|[Cloud Armor pricing](https://cloud.google.com/armor/pricing)|regional0.60/M、policy約5/月、rule約1/月、Standard。Enterpriseの包括料金や追加DDoSを混入させない|
|G-LB|[Load Balancing pricing](https://cloud.google.com/load-balancing/pricing)|検索経由で料金構造確認、本文取得失敗。regional externalとinternal proxyのmeter取り違え防止のため、0.025/h＋0.008/GiBはE。適用するSKU・課金方向は未確認|
|S-MON|[Lambda pricing](https://aws.amazon.com/lambda/pricing/)、[Scheduler](https://aws.amazon.com/eventbridge/pricing/)、[SNS](https://aws.amazon.com/sns/pricing/)|Lambda本文は取得。0.0000166667/GB-s、0.20/M requests等を仮計算。東京/大阪SKU精算とscheduler/SNS適用は未完（E）。Synthetics料金は採用しない|
|S-MAIL|[SES pricing](https://aws.amazon.com/ses/pricing/)、[privacy](https://aws.amazon.com/compliance/privacy-features/)|送信0.10/千通、data0.12/GB。各案共通でAWS東京SES API。国を限定した受信側保存/全転送の保証は未確認|
|S-AUTH|[Django auth](https://docs.djangoproject.com/en/dev/topics/auth/)、[session](https://docs.djangoproject.com/en/6.0/topics/http/sessions/)|frameworkのauth/sessionを国内SQLに配置する候補。外部IdPのMAU料金なし、保守/セキュリティ/CPUは内製責任。versionを決定していない。MFA/メール確認は実装済みではない|

Microsoft API取得filter：serviceName eq 'Azure Container Apps' / 'Azure Database for PostgreSQL' and armRegionName eq 'japaneast' and priceType eq 'Consumption'。WAFはcontains(productName, 'Application Gateway')を使用。全JSONを公開せず必要meterのみ保存。取得件数はページ内に収まりNextPageLinkなしを確認する。

## 精密単価/適用の未確認（出典先を示すが取得済みとしない）

|ID|公式の精算先|今回の扱い|
|---|---|---|
|S-NET|[AWS EC2 data transfer](https://aws.amazon.com/ec2/pricing/on-demand/)、[Azure bandwidth](https://azure.microsoft.com/en-us/pricing/details/bandwidth/)、[GCP VPC](https://cloud.google.com/vpc/network-pricing)|インターネット0.12/GB、AZ両端0.02/GB、国内地域間AWS0.09/Azure・GCP0.08は比較用E。実SKU/宛先/GB-GiBの違い、IP内包、routing料を未確認|
|S-OBS|[CloudWatch](https://aws.amazon.com/cloudwatch/pricing/)、[Azure Monitor](https://azure.microsoft.com/en-us/pricing/details/monitor/)、[Google Observability](https://cloud.google.com/stackdriver/pricing)|取込10GB/30日、10metrics/10alarms/1%traceに式を付けるがregional/時系列/traceの課金粒度はE。Azure公開meterも取得したが見積行への照合未了|
|S-SEC|[AWS Secrets Manager](https://aws.amazon.com/secrets-manager/pricing/)、[AWS KMS](https://aws.amazon.com/kms/pricing/)、[Key Vault](https://azure.microsoft.com/en-us/pricing/details/key-vault/)、[Secret Manager](https://cloud.google.com/secret-manager/pricing)、[Cloud KMS](https://cloud.google.com/kms/pricing)|秘密/鍵/操作回数のE積算。rotation時active versions増、跨社AWS credentials等の追加操作費未精算|
|S-DNS|[Route 53](https://aws.amazon.com/route53/pricing/)、[Azure DNS](https://azure.microsoft.com/en-us/pricing/details/dns/)、[Cloud DNS](https://cloud.google.com/dns/pricing)|2zones/2百万queryのE。DNS名へPIIを置かない。query logs/管理metadataの所在地を確認する必要|
|S-BACKUP|[RDS pricing](https://aws.amazon.com/rds/postgresql/pricing/)|100GB backupを全量有料計算、RDS無料含有枠に非依存。単価/削除後backup/meterのE|
|Z-STORAGE/G-STORAGE|[Azure Block Blob](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/)、[Cloud Storage](https://cloud.google.com/storage/pricing)|国内地域/冗長・版・操作・replicationのE。soft delete/default retentionによる35日越えを防ぐ設定/契約は未確認|
|S-CI|[ECR](https://aws.amazon.com/ecr/pricing/)、[ACR](https://azure.microsoft.com/en-us/pricing/details/container-registry/)、[Artifact Registry](https://cloud.google.com/artifact-registry/pricing)、[Actions billing](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions)|2GBimage/100分CI等のE、無料公開runnerの適合前提にしない。セキュリティscan・別地域資材保管の未精算あり|

## 採用前に残る証跡

1. 3社＋SES/受信先・DNS・ログ・鍵・CI/registryについて国内保存/転送範囲の確認。B-1は法令適合審査ではない。
2. 35日内の全copy/version/soft-delete/手動backupの消去と削除台帳の扱い。日数設定だけで物理消去保証とはしない。
3. 外部入口からログイン等の全依存を含む障害試験、片AZ100RPS/500人/p95、300秒安定・RPO時刻の実証（C承認後）。
4. GCP地域SKUと地域ALB、Azure WAF容量、AWS CPU credit、backup churn、非本番停止/再作成、外形監視の独自実装保守を精算。
5. B-1は全候補未実装。公開API/仕様調査はクラウドアカウント・請求書確認ではない。
