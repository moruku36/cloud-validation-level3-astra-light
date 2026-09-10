# C-0：移行条件・限定実験・承認事項の整理

最新2026-09-11：[CP1：最小C-1承認票・準備判定B](minimal-experiment.md)／[数量・単価・U・500円案](minimal-cost-model.json)／[実行記録](../../../evaluation/C-0-minimal-approval-run.md)。PR #16のLC1を継承し文書具体化完了。未回答bindingと例外承認待ち、実装/Planは次工程。実験未承認、C構築開始不可。以下のC-0/LC1時点の記録は履歴として保持する。

後続の[B-2限定設計補完LC1](../../B/B-2/limited-completion/README.md)は条件別文書更新として実施済み。今回承認されたのは4群の設計補完のみで、本C-0の実験承認票E1〜E12は未承認を維持する。次は同票の具体化・限定実験可否判断（文書のみ）の別依頼を推奨。以下はC-0時点の判断を保存する。

2026-09-10。**C-0の整理・文書化は完了。承認票は未承認、C構築開始不可、通常C移行は保留。** 初回66／B-2完了66／B-3修正後66の設計不合格、最終選定保留、人間採点・採用承認未取得を維持する。AWSは優先参考設計であり最終採用ではない。

- [移行阻害事項と試験の対応表](blockers.md)
- [A/B比較・推奨する次の1工程](decision.md)
- [C-0承認票・必要最小限の質問](approval.md)
- [実行記録・起点とGitHub状態](../../../evaluation/C-0-run.md)
- [引継ぎ](../../../handoff.md)／[資源台帳](../../../resource-inventory.md)／[Issue #9](https://github.com/moruku36/cloud-validation-level3-astra-light/issues/9)

今回の明示依頼により、過去文書の「C-0未開始」を整理工程に限り更新する。工程完了・設計合格・最終選定・人間採用承認・限定実験承認は別の状態である。既存C計画の「C-0合否＝承認済み」は満たしていない。整理完了を操作承認へ読み替えない。

根拠は[B-3レビュー](../../B/B-3/review.md)、[限定修正](../../B/B-3/revised-design.md)、[24要件対応](../../B/B-3/traceability.md)、[B-2試験定義](../../B/B-2/validation-plan.md)、[既存C計画](../../B/B-3/c-validation-plan.md)。B-2原文とB-3補足を併読し、既存設計・採点・試験IDは変更しない。クラウド操作、実装、試験、送信、マージは行わない。
