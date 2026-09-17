# B-2 選定・設計

**最新：[C-0後の限定設計補完LC1（必要4群）](limited-completion/README.md)**。条件付き文書補完完了、LC1は未採点。B-3の66/66/66点不合格・最終選定/人間採用承認/C移行保留を維持。次はC-0承認票の具体化・限定実験可否判断（文書のみ）を推奨し、自動実行しない。以下の金額/次工程表現はB-2当時の記録。

**最終選定保留。AWSを優先参考設計とするが、未承認の暫定案である。** 国内保存・削除の確認、必要容量と全依存の無人復旧、費用精算が残る。文書完成は設計合格・採用承認を意味しない。B-3正式評価・人間採点・C実証は未実施。

|7日PITRを最低復元窓とする共通条件付き案|税込基本/月＋未精算U|20%参考額＋1.2U|判断|
|---|---:|---:|---|
|AWS：Fargate×2＋RDS Multi-AZ|83,248円|99,898円|予算余地16,752円。ただし性能/運用増額は未精算|
|GCP：Run min2＋SQL Enterprise HA|101,933円|122,320円|東京DB単価確認後も概算超過1,933円。価格差で棄却確定しない|
|Azure：ACA＋PostgreSQL HA＋regional WAF|218,588円|262,306円|現代表案は予算未達|

初期本番＋最小非本番＋SES/外形監視を含む。為替150円/USD、税10%、無料枠等なし。7日はAI設計案で業務承認済みではない。B-1の30日PITRを必須条件から外したが、元資料・64/62/59点・重みは変更していない。

読む順序：
1. [selection](selection.md)：判断、逆転条件、確認責任の分類。
2. [design](design.md)・[構成図ソース](architecture.mmd)：実装を分解するための参考設計。
3. [recovery-observability](recovery-observability.md)：障害、保存/削除、監視。
4. [cost](cost.md)・[計算JSON](cost-model.json)：金額・差分・成長・未精算。
5. [validation-plan](validation-plan.md)：24要件とC証跡の対応。
6. [sources](sources.md)・[実行記録](../../../evaluation/B-2-run.md)・[handoff](../../../handoff.md)。

主な判断待ち：受信者メール側の国内保存範囲、7日を超えて論理破損に遡る業務上の必要性、内製認証/監視の担当・工数。いずれも未回答を承認に読み替えない。[Issue #9](https://github.com/moruku36/cloud-validation-level3-astra-light/issues/9)で追跡する。

次の1工程は明示指示後のB-3「評価・引継ぎ」。B詳細レポートをGitHubへ保存する。C予算/期限/操作許可はC-0で別途確定し、自動移行しない。
