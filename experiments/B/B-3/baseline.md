# B-3 評価対象の固定（レビュー・限定修正前）

2026-09-10。PR #12をGitHub APIで確認しOPEN/merged=false、head `b2/cloud-selection-design` の完全SHAが `cbcc26dc4d6f471e0934bb5fac7200411a038321` と確認。git fetch結果も一致した。このheadから`b3/evaluation-handoff`を作成した。

**B-3 PR比較先は`b2/cloud-selection-design`、未マージPR #12に依存。** mainは`ce6a1be764c7e46a233598618ef9a1baf9e5d2cd`だが、今回の起点ではない。PRはマージしない。

|評価対象|固定SHA|参照・役割|
|---|---|---|
|B-1事前比較基準|`4f486d2e1d2cf82fbb0571e440d31b7841a0580e`|[comparison-criteria](https://github.com/moruku36/cloud-validation-level3-astra-light/blob/4f486d2e1d2cf82fbb0571e440d31b7841a0580e/experiments/B/B-1/comparison-criteria.md)|
|B-1初回比較|`1812e6dc33d254be868b25b487ed962053a7f0d0`|[comparison](https://github.com/moruku36/cloud-validation-level3-astra-light/blob/1812e6dc33d254be868b25b487ed962053a7f0d0/experiments/B/B-1/comparison.md)|
|B-1完了・比較評価の原対象|`7c06ed0432a86b6a3c23db4eb85872d0e4591192`|[B-1 tree](https://github.com/moruku36/cloud-validation-level3-astra-light/tree/7c06ed0432a86b6a3c23db4eb85872d0e4591192/experiments/B/B-1)。AWS64/GCP62/Azure59は相対点で、B-3点へ転記しない|
|B-1追加図表の確認対象|`ce6a1be764c7e46a233598618ef9a1baf9e5d2cd`|[B-1 tree](https://github.com/moruku36/cloud-validation-level3-astra-light/tree/ce6a1be764c7e46a233598618ef9a1baf9e5d2cd/experiments/B/B-1)。後付け図であり事前基準や新業務要件ではない|
|B-2初回設計（I）|`7daa93c08be4508632af5d4669702a5bccb5bd67`|[実物tree](https://github.com/moruku36/cloud-validation-level3-astra-light/tree/7daa93c08be4508632af5d4669702a5bccb5bd67/experiments/B/B-2)。git objectの存在確認済み。初回を再構成しない|
|B-2完了（F）・B-3起点|`cbcc26dc4d6f471e0934bb5fac7200411a038321`|[実物tree](https://github.com/moruku36/cloud-validation-level3-astra-light/tree/cbcc26dc4d6f471e0934bb5fac7200411a038321/experiments/B/B-2)。PR #12最新headと一致|
|B-3限定修正後（R）|これから作成。確定commitはscores/runへ追記|I/Fを変更せずB-3/revised-design.mdの差分補足を追加する。架空の修正後は採点しない|

## 文書と優先順位

今回B-3指示→[正式業務回答](../../../docs/sources/business-answers-2026-09-08.md)・[24要件](../../A/A-1/requirements.md)→[正式補足](../../../docs/sources/supplement-2026-09-08.md)・[rubric](../../../evaluation/rubric.md)→今回B-3限定修正→固定したB-2本文→B-1原比較→説明用図の順。工程限定表現は今回指示で更新するが業務条件/合格基準は変更しない。

各版のB-2評価対象はREADME.md、selection.md、design.md、architecture.mmd、recovery-observability.md、cost.md、cost-model.json、sources.md、official-rates.json、validation-plan.md。I→Fの内容差分はdesign.mdのGCP逆転案追記とrecovery-observability.mdの退会outbox原期限追記。その他は同一内容（git diffで確認）。運用記録の根拠はevaluation/B-1-run.md、B-2-run.md、handoff.md、resource-inventory.md、Issue #9/コメント。

初回案は固定SHA参照で保存し大量複製しない。本baselineを独立commitしてから採点・限定修正する。自己評価はI/F/Rの存在する実物に対応、人間欄は空欄。指定GPT-6 Astra Lightの実識別は未確認。サブエージェント不使用。
