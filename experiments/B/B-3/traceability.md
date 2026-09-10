# 正式24要件の追跡

原要件は[requirements](../../A/A-1/requirements.md)、判断は[B-2 design](../B-2/design.md)・[selection](../B-2/selection.md)・[recovery](../B-2/recovery-observability.md)・[cost](../B-2/cost.md)。以下はF＋Rの設計レビューで、B-2判断を実測へ昇格させない。「根拠あり」は設計上適合の根拠があり実装合格とは別。「未確認」は要件全体を適合とする根拠不足。「未達」は既知の数値/条件不適合。Issue欄のH/D/Eは人間判断/設計差戻し/C実証待ち。[Issue #9](https://github.com/moruku36/cloud-validation-level3-astra-light/issues/9)を共通追跡先とし、試験IDは[B-2試験定義](../B-2/validation-plan.md)を継承、工程は[C計画](c-validation-plan.md)。

|ID|B-2判断・根拠|設計判定|証拠段階|残る判断/検証・B-3指摘|Issue分類/将来試験|
|---|---|---|---|---|---|
|REQ-01|3社同条件で比較、AWSは参考。selection/B-1 criteria|根拠あり|文書履歴確認済み|最終選定と再比較条件の人間判断|#9 H、B-3 review|
|REQ-02|writer commit→writer read、owner/session制御。design|未確認|設計根拠のみ|管理者画像更新経路/role確定、更新直後参照/他人拒否。F05|#9 D/E、T01/T02|
|REQ-03|private画像、SQL outbox/SES。design|根拠あり|設計根拠のみ|type/sizeと曖昧送信重複、worker回復、対象外機能不混入|#9 E、T02|
|REQ-04|1万→100万人とMAU/RPSを分離。design/cost|根拠あり|設計根拠のみ|row/index/backup容量の測定|#9 E、T03|
|REQ-05|10/100RPS15分、9:1、500人別モデル。cost|根拠あり|設計根拠のみ|通常継続時間/peak頻度はAI計算仮定。generator律速除外|#9 E、T04|
|REQ-06|API別p95≤500ms/error<1%、メール除外。validation-plan|未確認|計測計画のみ|通常/peak/片AZ残容量で性能根拠不足。F06|#9 D/E、T04|
|REQ-07|DB20GB＋2/月、画像100GB＋10/月、200GB転送。退会/復元台帳。recovery|未確認|設計根拠のみ|30日/35日、全version/clone/backup原期限、復元再削除。F02|#9 D/E、T05/T15|
|REQ-08|Tokyo/Osaka保存、TLSメール。design/sources|未確認|配置の設計根拠のみ|受信側、DNS/監査metadata、認証/log/backupの実範囲。技術だけで法令完了不可。F04|#9 H/D/E、T06|
|REQ-09|全主要flow外形、unknown別計上。recovery|未確認|計測設計のみ|暦月99.9%、依存障害/計画停止含む、共通盲点。F08|#9 D/E、T07|
|REQ-10|2AZ/自動置換、計画1800秒。recovery|未確認|時間配分の仮定のみ|影響→検知→復旧後実時間300秒安定終了、全依存/無人/片AZ。F06|#9 D/E、T08|
|REQ-11|外部成功応答台帳と復元DB比較。recovery|未確認|計測設計のみ|障害時刻−復旧最新確定data時刻≤300秒、整合/欠損。F06|#9 D/E、T08|
|REQ-12|AWS83,248円＋U、本番/非本番込み。cost|未確認（GCP/Azureは基本額未達）|算術確認済み、価格適用/数量条件付き|U・必要容量・変動余地。労務除外と負担評価を分離。F01|#9 D/E、T09|
|REQ-13|夜間即応なし、自動復旧前提。design/recovery|未確認|設計根拠のみ|専任1名/5開発者の担当・全依存自動復旧未成立。F06/F11|#9 H/D/E、T08/T10|
|REQ-14|managed container/SQL、K8s回避。selection|根拠あり|設計比較のみ|経験不足だけの排除ではない。教育/主副担当を承認・演習|#9 H/E、T10|
|REQ-15|1000RPSと登録100万人分離、将来予算別。cost/design|根拠あり|感度分析のみ|max6/追加18task例は保証なし、増強容量と費用の実証|#9 E、T11/T03|
|REQ-16|SG/private DB/secret/owner/ログ抑制。design|未確認|設計根拠のみ|auth管理権限/version/patch、保存削除、管理画像専用role。F02/F04/F05|#9 H/D/E、T12/T06|
|REQ-17|基盤/DB/AZ/region/WAF/CDN境界を比較。selection|根拠あり|文書確認済み|CDNなしは転送/性能が変われば再検討、選定保留|#9 D/E、T04/T08|
|REQ-18|IaC/OIDC/State分離、expand-contract rollback。design|根拠あり|設計根拠のみ|空環境再構築/lock/承認/互換rollback/移行演習|#9 E、T13|
|REQ-19|B-3で正式採点、B-1相対点は別。selection|根拠あり|[scores](scores.md)で採点手続確認済み|設計そのものは66点で不合格、人間欄空欄|#9 H/D、B-3 scores|
|REQ-20|公開文書/PR/Issue/固定履歴。B-2-run|根拠あり|文書・git確認、今回remote確認はrunに記録|公開範囲/リンク/PR head/baseを確認し完了|#9 E、B-3-run|
|REQ-21|工程限定・クラウド操作なし。B-2-run|根拠あり|取得可能な操作記録|A-1/B-2の工程名は今回B-3指示で置換。C/merge禁止維持|#9、B-3-run|
|REQ-22|C-0で予算/期限/権限、独立変更/cleanup。validation-plan|根拠あり|B-3で計画作成のみ|C予算/権限/例外保持承認前、実験開始不可|#9 H/E、T14|
|REQ-23|隔離PITR/正常更新救済、判断から4h暫定。recovery|未確認|計画時間のみ|救済不能・破損不明・台帳欠落時の損失/公開制御。F07|#9 H/D/E、T15|
|REQ-24|Osaka cold、30分/5分対象外。recovery/cost|根拠あり|方針/費用の設計根拠のみ|東京依存なしのimage/key/台帳復元、時間と損失限界を測る|#9 E、T16|

本番機能・性能・復旧・削除・国内保存について「実証済み」の要件はない。確認済みなのは入力/履歴/文書/計算/公開状態の該当範囲だけ。B-3は要件を緩和せず、設計合格を得るための条件は[scores](scores.md)のまま維持する。
