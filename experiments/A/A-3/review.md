# A-3 設計レビュー

2026-09-09。起点b5f5022、比較先a2/aws-design（PR #5未マージ）。初回設計81cab82とレビュー前b5f5022を保持。baseline/はレビュー前コピー、修正はrevised-design.mdとbudget.mdを優先適用する。A-2原稿は歴史証跡として変更しない。

## 結論
A-3レビュー工程は完了可能。Aの設計は**合格条件未達、採用承認保留**。監視費を加味すると初期税込10万円を超える。全依存のRTO/RPO・性能・個人情報所在地/削除の保証に未確認が残る。未実測だけを理由に設計採点を失格にはしないが、重要な根拠不足を4点以上へ引き上げない。重大禁止行為の発生は確認していない。

## 指摘と修正
|ID|指摘|最小修正|影響|
|---|---|---|---|
|F01|監視30USDに東京/大阪毎分Canary費が入らない|各地域1本の複数ステップCanaryに明確化し、実行料166.44USD＋他監視30USDへ訂正|初期小計約11.01万円、予備20%込約13.22万円。REQ-12未達|
|F02|5回の毎分成功は最初から最後まで4分の場合がある|復旧後の最初の正常応答から実時間300秒以上、開始を含む毎分6観測、途中失敗/欠測はリセット|RTO計測の早期成功判定を防ぐ|
|F03|2AZ指定だけでは各AZの常時容量を保証しない|AZ rebalancing明示、各AZ healthy task≥1を公開/デプロイの検査条件、欠損検知と自動補充。残存1taskで100RPS検証|task数増加なし、配置・容量は条件付き。補充成功は保証でない|
|F04|Lifecycle設定だけでは厳密な35日削除を証明できない|期限前削除・全version/複製/snapshotの残存照合、失敗時通知を追加。実際の消去期限は未確認|追加運用負担。backup上限35日を緩和しない|
|F05|削除台帳42日保持と退会30日削除の関係が未確定|PII台帳を稼働系要件の例外として扱わず、最小識別子の必要性・保持範囲を人間の承認事項とする|現在の台帳案は未承認、REQ-07適合は未確認|
|F06|ALB→task HTTPSは相手証明書を検証しない|暗号化と相手認証を区別、SG/限定target登録roleの境界を明記|mTLS達成等と主張しない。DB verify-fullは維持|
|F07|同じ常駐workerのSES処理が主要APIを圧迫し得る|worker concurrency≤1/task、短timeout・別接続枠、メールretry上限とbackoff|容量試験はoutbox処理込み。外部メール停止で主要APIを巻き込まない条件を追加|

今回指示の「RTOは検知から…含む」は検知工程を含める趣旨と解釈し、正式業務条件の**サービス影響発生から**を維持する。検知遅延を除外する緩和は行わない。

## 追加公式確認（限定）
- [CloudWatch東京料金表](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/ap-northeast-1/index.json)、[大阪](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/ap-northeast-3/index.json)：各0.0019USD/run。canary-prices.jsonにSKU・発行日を保存、確認日2026-09-09。
- [Canary概要](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries.html)：定期的なAPI/E2E確認。実行料以外のLambda/S3/log等は別費目。
- [S3 Lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/troubleshoot-lifecycle.html)：非同期で物理削除に遅れ得る。
- [ALB target TLS](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)：target証明書の検証なし。
- [ECS AZ rebalancing](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-rebalancing.html)：自動再配置。宣言だけで故障時容量の証明にならない。
他の価格/仕様はA-2 sources.md・抽出JSONを再利用。追加調査は上記で打ち切り、残りは未確認として判定する。法令適合確認・実装・性能/障害試験なし。
