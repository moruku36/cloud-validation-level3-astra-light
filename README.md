# クラウド検証LEVEL3

保存先：moruku36/cloud-validation-level3-astra-light（一般公開）。
状態：A-1〜A-3完了。設計評価61→65点で合格条件未達、採用承認保留。クラウド作成なし。Aレポートの人間確認後、指示があればB-1。

- [LEVEL3-A 詳細検証結果レポート](experiments/A/final-report.md)（過去成果物の集約、再設計・再採点なし）

- [要件定義・不足部分](docs/requirements.md)
- [共通指示](docs/execution-policy.md)
- [原本の取得可能な本文](docs/sources/shared-chat.txt)
- [再開情報](handoff.md)
- [リソース・費用](resource-inventory.md)
- [準備・操作記録](evaluation/repository-preparation.md)
- [A-1依頼受領記録](evaluation/A-1-intake.md)
- [初回案](evaluation/snapshots/pre-repository/)

工程：A-1→A-2→A-3→B-1→B-2→B-3→C（別途定義）。1回1工程、PRは指示なしにマージしない。

## A-1 要件整理

- [要件ID・受入条件](experiments/A/A-1/requirements.md)
- [重要質問・回答台帳](experiments/A/A-1/questions.md)
- [仮定・制約・リスク](experiments/A/A-1/assumptions-risks.md)
- [追跡表](experiments/A/A-1/traceability.md)
- [正式補足](docs/sources/supplement-2026-09-08.md)
- [評価表（未採点）](evaluation/rubric.md)
- [人間の介入](evaluation/human-intervention.md)
- [A-1操作・検証記録](evaluation/A-1-run.md)
- [回答対応Issue #2](https://github.com/moruku36/cloud-validation-level3-astra-light/issues/2)

初回案はA-1ブランチの最初の成果物コミットで識別。レビュー後版はまだない。準備PR #1は未マージのため、A-1 PRはそのブランチを基点にする。

A-1：[PR #3](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/3)、[初回案6731042](https://github.com/moruku36/cloud-validation-level3-astra-light/commit/6731042)。初回案を保持し、正式回答反映版を後続コミットで識別。設計レビュー後版は未作成。

- [正式業務回答](docs/sources/business-answers-2026-09-08.md)
- [今回の回答反映・完了確認](evaluation/A-1-completion.md)

A-1完了時の次回工程：A-2（現在の次回は下記A-3）。残る設計評価事項は[Issue #4](https://github.com/moruku36/cloud-validation-level3-astra-light/issues/4)。

## A-2 AWS設計

- [設計・3案比較](experiments/A/A-2/design.md)
- [構成図](experiments/A/A-2/diagram.md)
  - ![実験構成図: moruku36/cloud-validation-level3-astra-light (AWS構成)](experiments/A/A-2/architecture.jpg)
- [復旧・監視・運用・IaC方針](experiments/A/A-2/recovery-operations.md)
- [月額概算](experiments/A/A-2/cost.md)
- [公式出典](experiments/A/A-2/sources.md)
- [判断と要件ID](docs/decisions/ADR-A2-001.md)
- [Issue #4対応・未検証](experiments/A/A-2/issue4.md)
- [実行・訂正記録](evaluation/A-2-run.md)

初回設計81cab82、後続は算術表記と追跡情報の訂正。次回はA-3のみ（まだ実施していない）。

[A-2 PR #5](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/5)はA-1ブランチを比較先とし、PR #3に依存します。未マージ。

## A-3 AWS設計評価

A-3レビュー完了。設計自己採点は初回61点・修正後65点、合格条件未達・採用承認保留。A-2の約8.27万円は監視費不足を含む旧見積。修正版は約11.01万円、予備費20%込約13.22万円。

- [レビュー・追加根拠](experiments/A/A-3/review.md)
- [24要件対応・判定](experiments/A/A-3/traceability.md)
- [修正仕様](experiments/A/A-3/revised-design.md)
- [費用監査・感度・削減案](experiments/A/A-3/budget.md)
- [初回/修正後採点](experiments/A/A-3/scores.md)
- [人間判断・C試験](experiments/A/A-3/validation-handoff.md)
- [レビュー前保存版](experiments/A/A-3/baseline/README.md)

次回は人間の判断待ち。Bには自動で進まない。

[A-3 PR #6](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/6)（比較先a2/aws-design、PR #5依存、未マージ）。
