# B-3限定修正（R）

2026-09-10。適用対象は[固定B-2完了版](baseline.md)。B-2の原文は保持し、以下を優先する補足だけを追加する。クラウド構成・価格数量・業務要件は変更しない。実装も実証も行っていない。

|指摘|修正前の状態|限定変更|結果・採点への影響|
|---|---|---|---|
|F02 削除の複製先|国内2拠点の期限管理はあるが、version削除/複製失敗時の実行条件が不十分|全bucketのcurrent/noncurrent version、delete marker、未完了multipart、replication pending/failedを個別棚卸し。元と先へ独立した削除・確認を計画する。CRRやLifecycleだけで期限内消去と判定しない|説明を補強。自動収集・失敗時処理と事業者内部消去は未確認、Security/DRは3のまま|
|F03 RDS保持範囲|sourcesのDB instance保持可能範囲「1–35日」|正しくは0–35日。0は自動backup無効。本案8日を変更しない。停止期間は保持日数に算入されず、復元instanceも保持設定を点検する|仕様誤記訂正。8日案の採用承認・実証にはならず点数不変|
|F04 DNSログ所在|国内ログ設計とglobal metadata未確認が併存|Route53 public authoritative DNS query logsはCloudWatch us-east-1。国内保存を確認できるまで当該query loggingを有効化する案を採用しない。国内app/probeの観測と区別し、control-plane metadataの所在確認は別に残す|国内保存完了とは判定しない。監査網羅性とのトレードオフが残るため点数不変|
|F05 画像更新権限|通常appのS3読取権限に対し管理者更新経路のIAMが未確定|通常appの権限拡大で穴埋めしない。管理者画像取込の専用role、承認主体、許可prefix、形式/上限検査、監査の設計をB-2差戻しに明記|新role実装や構成確定ではない。Architecture/Securityは3のまま|
|F10 cleanup完了の定義|課金資源を日跨ぎ前に削除する方針|KMSは7–30日の削除待機＋最大24時間程度の処理遅延を追跡。PendingDeletionを削除済みと書かない。事前承認された残存例外、期限、後日確認をC-0で決める。必要な暗号化資源/Stateを先に失わない|C計画の矛盾を除去。復旧実証や採用承認ではなく、正式点数不変|

根拠（2026-09-10確認）：[S3 expiration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html)、[複製対象外の削除](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-what-is-isnot-replicated.html)、[RDS retention](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html)、[Route53料金・query logging](https://aws.amazon.com/route53/pricing/)、[KMS削除](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html)、[KMS料金](https://aws.amazon.com/kms/pricing/)。KMS削除待機中は課金されないが、取消時は待機期間も課金される。disabledは無料化しない。

F02は非current化時点からの期限と退会日起算の期限を混同しない。Lifecycleの非同期処理、複製pending/failedのexpiration除外があるため、設定日数だけで30日/35日適合としない。退会台帳28日、復元資材14日というB-2案は内部設計値であり、正式上限の置換ではない。遅延削除・台帳欠落・再backup時に原期限を維持できない場合は復元公開を止めるが、その停止と可用性の両立はB-2で解決する。

全面再選定・新構成への変更は行わない。メール受信側の保存範囲、最低PITR期間、内製保守体制、不可逆損失の受容は人間判断待ち。[review](review.md)・[Issue #9](https://github.com/moruku36/cloud-validation-level3-astra-light/issues/9)を参照。
