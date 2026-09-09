# B-2追加根拠・再利用・未確認

確認日2026-09-10（Asia/Tokyo）。公式公開情報の読取りのみ。クラウドアカウントAPI/CLI・課金環境操作なし。旧仕様の再調査は結論に関わる箇所へ限定した。

|ID|公式URL / 保存証跡|確認した内容・限界|
|---|---|---|
|B2-GSQL|[Cloud SQL pricing](https://cloud.google.com/sql/pricing)、[必要単価の抽出](official-rates.json)|公式HTMLのJSON dataを静的解析、MySQL/PostgreSQLタブの東京とedition見出しを照合。Enterprise General Purpose HA CPU0.1074/h・RAM0.0182/GiB-h、Plus N2 HA0.1396/0.0237、SSD single0.221/HA0.442、backup0.104。割引列を使わない。catalog SKU ID・実適用請求は未確認|
|B2-GLB|[Cloud Load Balancing pricing](https://cloud.google.com/load-balancing/pricing)、[東京表](official-rates.json)|外部LB東京はin/out各0.012/GiB。内部proxy0.008を使わない。forwarding0.025/hはページ料金構造を確認したがregional適用精算はE。serverless NEGでRun outboundを重複加算しない|
|B2-GPITR|[Cloud SQL backup options](https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/backup-options)|Enterprise logs最大7日、Plus最大35日、日次backup世代は別。7日logsに8backupを推奨。default backup locationに頼らず国内custom location。手動backupの無期限に注意|
|B2-RRET|[RDS retention](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html)|DB instance保持1〜35日。停止中時間が保持計算から除かれる。日数設定だけで全snapshot年齢保証にしない|
|B2-S3EXP|[S3 expiring objects](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html)|versioningの旧版/delete marker、非同期削除を区別。期限消去の設定値を物理消去の実績としない|
|B2-SES|[SES data protection](https://docs.aws.amazon.com/ses/latest/dg/data-protection.html)|default opportunistic TLSは平文fallbackがあり、require設定候補を追加。受信者側所在地/全転送保証ではない|
|B2-SESDEL|[SES personal data deletion](https://docs.aws.amazon.com/ses/latest/dg/deleting-personal-data.html)|account suppression宛先は明示削除まで保持。event宛先にもPIIあり。削除対象へ追加。内部queue/全metadata保持と所在地は未確認|
|B2-SESENC|[SES encryption at rest](https://docs.aws.amazon.com/ses/latest/dg/encryption-rest.html)|暗号化の説明を確認。ただし送信全データの国内保存/期限保証をこの資料から得られなかった|
|B2-ALBTLS|[ALB target groups](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)|HTTPS target証明書は検証されない。SG/target登録の制約とTLS peer認証を区別|

公式価格HTMLは一時作業領域に保存、GitHubには必要な数値・URL・HTML SHA256・JSON pathのみ保存した。取得した外部scriptを実行していない。SQLページはweb取得が容量超過、公開HTML直接取得で解決した。ページ全部/第三者記事を転載しない。

## 再利用

[B-1 sources](../B-1/sources.md)のA-S01〜07（東京RDS/Fargate/ALB/S3/WAF/IPv4）、Z-RATE（Azure公開19meter）、G-RUN/G-ARMOR、S-MAILを2026-09-09取得根拠として再利用。SKU/容量は[B-1 cost-model](../B-1/cost-model.json)と今回JSONに追跡する。主要価格を一日後の確認済みと偽装せず、再利用日を明記した。

HA/failover、ECS AZ rebalancing、Cloud Run zone分散、Azure zone冗長はB-1で参照した公式仕様を継承。typical failover時間はSLO上限ではない。Django等の認証方式もB-1の候補で、version選定/実装/セキュリティ試験完了ではない。

## 未確認を維持する事項

S-NET/S-OBS/S-SEC/S-DNS/S-CIのregional meterと実量、GCP regional forwarding/IP、Azure managed networking、国内別region資材費はE/U継続。AWS縮退性能/CPU credit、SES・DNS・監査metadataの所在地/期限、台帳と物理消去の完全性、夜間全依存復旧、月間SLOは公式料金取得では解消しない。

共有ChatGPTリンクはwebでCache missのため内容を取得できなかった。引継ぎは添付指示とmain正式資料、PR #8/#10/#11・Issue #9の現行API情報に基づく。取得できない会話を読んだと記録しない。
