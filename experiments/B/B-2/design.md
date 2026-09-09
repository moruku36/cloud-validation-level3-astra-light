# AWS優先参考設計（未承認）

適用条件・代替は[selection](selection.md)。図は[architecture.mmd](architecture.mmd)。実装/SKU容量の適合は未確認。単一WebアプリとPostgreSQLを採用候補にし、OS/Kubernetes運用を増やさない。VMはOS保守、Kubernetesはcluster保守が増えるため初期案から外す。NoSQLは本人強整合とtransaction設計を別途検証する必要があり、SQLの容量/費用が成立しない時の再設計候補とする（REQ-01/02/14/17/18）。

## 配置・容量・データ経路

|部品|候補・配置・容量|役割/制限|
|---|---|---|
|公開DNS/TLS/入口|Route53、ACM、東京ALB＋WAF、2AZ|HTTPS443のみ公開、80はredirect。WAF ACL1、5課金rulesを予算枠としmanaged groupとrate制御の実課金をC前精算|
|Web/auth/mail worker|ECS Fargate Linux ARM、各1vCPU/2GiB、2taskを東京2AZへ分散|最大6は費用検討用で容量予約ではない。task内Webと小さなoutbox workerを分離プロセス。health/readiness・起動時間・ARM imageをCで確認|
|DB|RDS PostgreSQL db.t4g.medium、2vCPU/4GiB、Multi-AZ、gp3 50GB|private subnet2AZ、同期standbyはread処理に使わない。20GB＋auth/session/indexを収容する仮定。burstable CPU credit、memory、IOPSを未確認|
|画像|S3 Standard東京private、live100GB＋version20GB|管理者提供画像のみ。GetObject→app streaming→ALB。直接公開URL/署名URLを利用者へ出さずWAF迂回を防ぐ|
|メール|SES東京API、1万通/月仮定|DB outboxが永続キュー。受信者側所在地は判断待ち。メール停止中も既存利用者loginを成立させる|
|監視|AWS東京/大阪のScheduler＋Lambda、512MiB、10秒/flow見積|2地点毎分・10HTTP step、public DNS/HTTPSから測定。通知SNS、ログCloudWatch。共通provider障害の盲点あり|
|backup/資材|東京native backup、大阪S3 dump50GB/画像120GB、ECR image2GB、KMS/Secrets|cold restore。大阪鍵で利用可能な形で保管、東京鍵だけへの依存を禁止。コピー成功・鍵使用証跡が必要|
|非本番|別AWSアカウント/VPC、単一task1vCPU/2GiB＋RDS small single、32GB|月176hの1共有環境、ALB/WAFとdiskは常設、画像5GB/backup10GB。合成データのみ。DBの停止7日制限と休日自動起動を運用監視|

公開入口→private target IP→DB writerが主経路。taskはpublic subnet/public IPv4でAWS公開APIへのegressを確保し、受信はALB SGだけ。NAT費用は採用なし。S3同地域はGateway Endpoint候補、SG egress443のprefix list・endpoint/bucket policyを揃える。DB5432はapp SGだけ。S3はBlock Public Access、bucket owner enforced、TLS必須、IAM対象prefix制限。全task outbound443は宛先サービスをアプリ設定とIAMで制限するがSGだけではFQDN制限できない。egress proxy/PrivateLinkを追加する場合は費用再算定（REQ-08/16/17）。

初期2taskの各1taskが100RPS＋静的要求＋auth処理を処理できるという証拠はない。500人は同時実行数ではない。pool上限候補はWeb1taskあたり20、worker5、最大6task時150＋管理予約10=160接続。実際のDB max_connections/メモリを確認し、超過前にqueue/backpressureへ。CPU60%継続5分、memory70%、接続70%、free disk30%を増強検討の仮閾値とする。自動scale後も残1AZをCで検証、台数だけで性能を判定しない。

## 認証・本人整合・画像・メール（REQ-02/03/06/16）

- 認証は保守対象frameworkの標準auth（Django候補）＋server-side SQL session。採用versionとMFA拡張はC前にサポート期間/ライセンス/保守者を確認し固定する。独自暗号方式は作らない。passwordの安全なhash、login rate制御、汎用エラー、CSRF、Secure/HttpOnly/SameSite cookie、login時session rotationを必須タスクにする。
- 利用者は認証user IDからowner scopeを決定し、入力owner IDを権限根拠にしない。管理者は別role＋MFA、操作ごとに認可、一般userから権限昇格不可。管理role付与は別承認。セッション有効期限候補12h/idle30分、全session失効をlogout-all/password変更/退会/管理無効化時にwriterへ反映し、次要求でもwriterで確認する。
- プロフィール/お気に入り更新とoutbox記録は同一transaction、commit完了後に成功応答。次の参照はwriter、個人応答はprivate/no-store。favorite(user,content)一意、request idempotency keyと結果を同一transactionで保持。同時更新はversion比較で競合を409へ。失敗transactionを成功に見せない。
- 画像は業務参照の内容IDから固定keyへ解決し任意URLをfetchしない。上限5MiB/枚、JPEG/PNG/WebP等は設計仮定で管理者と調整。MIME実体/サイズ/画像decode安全性を検査し、変換時はmetadataを除去。app streamingの接続占有/転送/p95への影響を試験する。CDNはglobal cacheの所在地確認と費用/負荷改善が必要になった時点で再比較。
- outboxはevent UUID・attempt・next_attempt・lease_until・statusを保持し、複数workerがleaseで排他取得。SES timeout/429/5xxは指数backoff＋jitter（1分→上限1時間、24時間で要対応）。恒久拒否/bounceは再送停止。メール送信とDB成功記録は原子的でないため、SES受理後timeoutは重複し得る。同じeventを新規生成せず、曖昧送信を識別・監視し、exactly-onceを保証しない。
- 配信完了はAPI p95外。登録確認/password resetがメールに依存する範囲を別監視し、既存loginのSLOから認証処理自体を除外しない。本文はPIIを極小化し、tokenは短命/一回使用/hash格納。受信先TLSをrequireに設定する候補（非TLS受信先へ平文fallbackさせない）。TLSは保存場所の証明ではない。

## Security / IAM・所在地

|主体|権限境界|
|---|---|
|app task role|対象画像Getのみ、必要secret読出/KMS decryptのみ。DB app roleは通常DML、DDL/snapshot/鍵削除不可|
|mail worker|対象送信identityのSES Sendのみ、送信対象outboxだけ。suppression削除は別cleanup role|
|ECS execution role|限定ECR pull/起動secret/log stream。app権限と混同しない|
|backup job|DB read/export、DR対象prefix write。既存backup一括削除や鍵削除は不可|
|cleanup/restore|期限制御対象の削除と隔離restoreに分割。本番公開route変更は人間承認、通常運用roleでは不可|
|CI read/plan / deploy|GitHub OIDC短命認証、aud・repository・branch/environmentを限定。fork PRはread-only検査、cloud権限なし。plan roleはread主体、apply roleは承認環境からのみ|
|人間管理者|個別ID＋MFA、一時昇格。rootは通常使用せず復旧手順を別管理|

ALB→target HTTPSは暗号化されるがALBはtarget証明書を検証しない。通信相手の制約はSG/target登録IAM/VPC境界で担保する候補でありmTLS保証と記載しない。DBはTLS verify-full＋RDS CA更新手順、AWS SDKはhostname/証明書検証とSigV4。TLS復号後のログにcookie/header/query/body/SQL bind値を出さない。

東京にDB/S3/log/trace/secretsを配置し、大阪のbackup/registryは別権限・別regional key。利用者氏名・メール・IP・認証tokenをresource名/tag/metric label/URLへ入れない。ALB生アクセスログはquery/IPを含むため初期案では保存しない。WAFはredactionに加えsampled requests・body captureの抑制を検証する。匿名化できない必須監査metadataはU01として保存先/保持を確認し、抑制できたと断言しない。

## IaC・配布方針（実装・実行なし、REQ-18/20/22）

将来IaC対象はnetwork/SG、ECS/ALB/WAF、RDS parameter/backup、S3全世代期限、IAM/KMS/Secrets、DNS、監視/復旧通知。prod/dev/DRは別state、国内private versioned S3 backend、state lockingを使う。stateにも機密値が入り得るためpublic GitHubには置かない。backend方式/versionのlock対応をC前確認、機密planは国内暗号化保管・短期削除、PRにはマスク済み要約だけを記録する。

PRでformat/validate/policy/secret scan/image vulnerability検査→read-only plan→人間承認→短命apply/deploy。現在workflowもIaCも作らない。image digestで固定し前の正常imageを国内2地域に保持。rolling minHealthy100%/max200%候補、health悪化時自動rollbackの条件をCで実装・検証。DBはexpand→互換期間→contractを分け、破壊migrationをapp rollbackと同時に実行しない。復旧pointに対応するschema/image/依存lock/CA/設定を対応付ける。

GitHub/CI停止中も現行taskは継続、再配置に必要なimage/secretはAWSから取得できる設計。地域停止では大阪の資材とstateバックアップから再構築するがIAM管理API/国内quota/鍵が使えないケースは時間不明。移行時はOCI image、PostgreSQL dump、object inventory、outbox/session無効化を引き継ぐ。IAM/WAF/DNS/monitor/stateはprovider別再作成が必要。

## 体制・運用負担（REQ-13/14）

開発5名のうちauth担当1名・副担当1名、probe担当1名を割り当てる案。専任1名に認証コードまで集中させない。人数追加を前提にせず正式な割当は未承認。初期auth hardening/MFA/失効に5〜10人日、probe/欠測/復旧判定に3〜5人日、継続auth/probe更新8〜16h/月＋基盤/restore/容量管理16〜24h/月を計画仮定とする（人件費は予算外、実績なし）。

日中は毎営業日アラーム/費用/backup欠損/期限超過を確認。週次脆弱性/認証ライブラリ確認、月次patchと鍵/証明書期限・復元演習、四半期AZ/DR演習。夜間はmanaged restart/DB failover/既知正常revision rollbackと通知のみ。誤DNS/鍵無効化・不明な論理破損・全image欠落は自動修復を約束せず翌営業日対応となり、対象障害で30分を超えるならREQ-10未達。managed IdP/監視へ変更する場合も同じ所在地/削除/SLI要件で予算を再計算する。
