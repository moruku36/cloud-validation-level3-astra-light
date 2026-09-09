# A-2 AWS単一クラウド設計 v0.1 — 初回案

2026-09-09。起点1745dfefe71e11a9df077eb247982f0f5f7616d7、PR #3未マージ、a2/aws-designはorigin/a1/requirementsから分岐。A-3採点・実装・クラウド作成なし。

## 判断
ECS/Fargate ARM＋RDS PostgreSQL Multi-AZを**条件付き採用**。一般Web開発・SQLの運用を活かし、管理対象OSを減らし、同期DB待機系と常時2AZのアプリで夜間の手動復旧依存を減らす。全要件適合を宣言するものではない。性能、認証依存の復旧、費用変動余裕に未検証・不足がある。予算見込みはcost.md、主要未達はissue4.md。

## 最大3案の比較（同じ負荷・国内保存・非本番・認証等を含む）
|案|基盤・データ|長所|短所/復旧/費用|判定・逆転条件|
|---|---|---|---|---|
|A|ALB＋Fargate常時2AZ＋RDS PostgreSQL同期Multi-AZ|SQL整合性、コンテナ可搬性、OS保守削減、常時容量|RDS/認証の地域障害・CPUクレジット・単一writer、固定費。基本約8.27万円、余裕込み約9.92万円|条件付き採用。予算リスクを解消できなければ承認不可|
|B|ALB＋EC2 Auto Scaling 2AZ＋同じRDS|アプリ互換、継続負荷では費用低下の余地|OS/AMIパッチ・起動時間・容量補充を専任1名で維持。基盤費は未取得のためA基盤72USDの代わりにVM/EBS計60〜110USDを仮置き、同じ他費目で約8.1〜8.9万円、余裕別|不採用。成熟したAMI運用と確定価格で有意な節約が出れば再比較。VM価格の確認不足を有利な根拠としない|
|C|Regional REST API Gateway/WAF＋Lambda＋DynamoDB、Cognito、国内S3|サーバー/DB容量運用低減、アクセスパターン固定なら強い|500msのcold start対策、GSIの結果整合性、一覧クエリ/二次索引設計と移行負担。月約2,835万動的要求でゲートウェイ＋実行＋ウォーム容量＋DBの従量費が変動|有力代替だが初回は不採用。クエリを固定でき、実測・公式見積でAより余裕を持って10万円以内なら逆転。『必ず安い』とは扱わない|

Cの費用はゲートウェイ単価3.5〜4.5USD/百万要求、Lambda 1GB×0.05〜0.2秒/要求、ウォーム同時10〜30、DB/backup20〜60USDという**未確定比較パラメータ**で概ね同等〜上振れを想定する（料金引用ではない）。正式な比較見積がないため、費用のみでCを排除しない。今回の選択はSQL/可搬性と常時容量による遅延予測性を重視。3案以外に案を増やさない。

Kubernetesは不採用：今回のCRUD・専任1名・本番経験なしに対し、独自スケジューラ/CRD/多数チーム境界の必要性なし。ECSで配置/更新を実現。Kubernetes標準化が事業条件になれば費用と運用体制を再評価。

## 配置と容量（性能保証ではなくC検証の開始サイズ）
東京ap-northeast-1、異なる2AZ。ALBとFargateは両AZ。各AZ1タスク、1vCPU/2GB ARM、最小2・最大6、片AZの1タスクで100RPSを処理できることを検証条件にする。失敗時は増量・増台で再見積、未検証のまま達成としない。通常CPU50%目安と要求数でscale-out、scale-inは5分以上安定してから、最低2を維持。障害復旧をscale-out成功だけに依存させない。
RDS PostgreSQL db.t4g.medium、50GB gp3、同期Multi-AZ（readable standby型ではない）。使用20GB＋2GB/月、インデックス/空き/WALを別途監視。同期commit、業務書込はcommit後にのみ成功を返す。接続プール各task最大10、6taskでも60＋管理/worker余裕、実際のDB上限は起動設定確認。CPU credit消費が継続するなら非バースト型へ変更して再見積。
SQL採用：ユーザー/コンテンツ/お気に入りの一意性、外部キー、トランザクションを自然に表す。本人参照はwriterから読み、本人のプロフィール・お気に入りは共有キャッシュ禁止。更新version/ETagと冪等キーでリトライ重複を防ぐ。read replica・Redisは初期不採用。DB以外にセッション正本を置かない。

## 通信・信頼境界
- Route53はDNSのみ。API/HTML/画像は東京ALB HTTPS→Fargate→東京private S3またはprivate RDS。画像は認証不要の公開コンテンツでも保存条件を維持。
- CloudFrontは初期不採用。世界のedge cacheと地域制限は国内保存保証と同義でない。国内保存制約を無断緩和せず、画像200GB/月では東京配信の費用を許容。国内限定保存を公式に確認できる配信方式か、公開画像に対する条件変更の承認が出れば再評価。
- NAT固定費を避け、**タスクにpublic IPv4を割当**。SG ingressはALB SGからアプリportのみ、SSHなし、DBはpublic access無効・DB SGはtask SGのみ。public IPは外向きAWS API用であり直接API公開の許可ではない。TLSはALB終端、taskへ再暗号化、DB TLS verify-full。
- S3 gateway endpointでprivate bucketへIAM限定アクセス。ECR/logs/SES/CognitoはTLS regional endpoints。タスクegress443は必要先、RDS5432とDNSを限定（AWS公開APIの宛先制限には維持負担がある）。CのPublic IP禁止条件ではprivate subnet＋2AZ NATまたは複数VPC endpointsへ変更する費用・到達性検証が必要。今回はその追加条件を前倒ししない。
- WAF RegionalをALBへ。標準マネージドルール＋rate limit、IP単独で500人を誤遮断しない閾値を負荷試験で検証。Bot Control等有料追加は初期不採用、必要なら再見積。body size上限、CSRF対策、CORS、認可はアプリ責務。

## 認証・データ所在地・メール
Cognito Lite user pool東京、アプリの独自ログインUIからregional API利用。hosted/managed loginのCloudFrontを避け、SMS/海外analyticsなし、SES送信元を東京ARNへ明示。管理者は別権限とTOTP MFA、一般ユーザーはpassword policy/rate制限、トークンの署名・aud/issuer/期限を検証。アプリ認可はユーザーsubと所有権照合。Cognito保存先は東京だがログインサービスの内部AZ failoverの30分上限は検証できていない。
SES東京で10,000通/月を仮定、メールbodyにプロフィール等を載せず必要最小限の宛先とリンク。メールは受信者サーバーへ転送されるため、その保存地域まで東京に保証できない。REQ-08の『外部保存転送先確認』の未確認範囲として受信先/処理契約をA-3でレビューし、全保存コピー国内が必須なら未達とする。法令適合完了は宣言しない。
通知はDB transactional outbox→同じ常駐タスクの競合安全worker→SES、送信後mark。at-least-onceで送信後mark前停止時は重複の可能性、メッセージIDで追跡。アプリ更新成功はメール完了待ちにしない。outbox最大滞留15分で通知、平常配信目標5分は設計仮定。退会時outbox宛先も削除。

## Security/IAM
本番と非本番をAWS accountで分離。非本番合成データのみ。人間はIAM Identity Center/MFA・日中の権限昇格、root使用禁止・緊急手順を保存。アプリtask roleは特定S3 prefix/SES identity/secret ARNのみ、execution roleと分離。RDS/S3/backup/Stateは暗号化、KMS key削除保護、DB秘密はSecrets Manager、GitHubに鍵やStateを置かない。
ログはcookie/token/email/nameを出力しない。URL queryにPIIを載せず、WAF sampled requestsは無効、WAFログはredaction/filter。ALB access logにはIP等が残り得るため初期は無効、CloudWatch集計とサニタイズ済みアプリ監査を使用。必要な生ログは保存場所・保持・承認を再設計。アプリログ14日、PIIなし監査90日を仮定（業務backup35日と混同しない）。管理/API監査はCloudTrail東京S3、秘密混入を抑止。
