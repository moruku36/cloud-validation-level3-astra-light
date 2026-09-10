# B-3正式自己評価

I＝[初回実物](https://github.com/moruku36/cloud-validation-level3-astra-light/tree/7daa93c08be4508632af5d4669702a5bccb5bd67/experiments/B/B-2)、F＝[B-2完了実物](https://github.com/moruku36/cloud-validation-level3-astra-light/tree/cbcc26dc4d6f471e0934bb5fac7200411a038321/experiments/B/B-2)、R＝F＋[限定修正の固定commit](https://github.com/moruku36/cloud-validation-level3-astra-light/blob/c0cf660d14af3ed67559a1d8d0244ddf4f164fd7/experiments/B/B-3/revised-design.md)。R SHA：`c0cf660d14af3ed67559a1d8d0244ddf4f164fd7`。比較対象の固定は[baseline](baseline.md)。

5段階は1欠落/重大誤り、2大幅修正、3概ね妥当だが重要根拠不足、4根拠/トレードオフが明確で軽微修正で採用可能、5さらに感度分析/適切な検証の裏付け。総合＝Σ配点×評価÷5。[rubric](../../../evaluation/rubric.md)と今回指示を適用。人間欄は空欄。

|項目|配点|I|F|R|加重点 I/F/R|根拠・不足（各版共通、差分は下記）|人間評価|
|---|---:|---:|---:|---:|---|---|---|
|要件理解|15|4|4|4|12/12/12|正式24要件、初期/成長/暫定目標を区別。保留を明記。[traceability](traceability.md)、B-2 selection。未知を隠さず条件変更なし||
|Architecture|15|3|3|3|9/9/9|container/SQL/2AZの理由はあるが依存網/管理画像更新と実容量が未完成。review F05/F06||
|Security/IAM|10|3|3|3|6/6/6|最小権限/TLS/PII抑制に根拠。保存/転送/全世代削除、auth保守境界不足。F02/F04/F05||
|Availability|10|3|3|3|6/6/6|1800秒の定義正しい。片AZと全依存の無人復旧成立根拠不足。F06/F08||
|Scalability|5|4|4|4|4/4/4|1000RPSと100万人を分離し容量/費用増/見直し条件明示。未実測なので5ではない。B-2 design/cost||
|Cost|10|3|3|3|6/6/6|全体内訳/感度分析/税と為替は追跡可。ただしU/性能必要容量未確定で予算適合未確定。F01||
|Operations|10|3|3|3|6/6/6|平日日中/無人前提を認識。auth/probe担当とpatch/休暇時負担未承認。F11||
|Backup/DR|10|3|3|3|6/6/6|国内cold/PITR/再削除設計あり。正常更新救済/原期限/全資材復元の根拠不足。F02/F07||
|Observability|5|3|3|3|3/3/3|主要flow外形とunknown分離あり。同一provider盲点/連続性/ログ所在地未解決。F04/F08||
|Complexity|5|4|4|4|4/4/4|Kubernetes回避と内製auth/probeの負担、managed代替との交換条件を開示。運用成立は別の3で評価||
|Vendor lock-in/移行性|5|4|4|4|4/4/4|SQL/container/dump/schemaとimage/鍵の依存分離、移行限界を明示。移行演習未実施で5ではない。B-2 design/recovery||
|合計|100||||66/66/66|||

I→FはGCP代替経路/IAMと退会outbox原期限の2段落が追加された実際の別版。改善はあるが評価段階を跨がない。F→Rは誤記・削除/DNS/cleanup説明を補足した実際の別版で、根本的設計根拠や人間判断を補完できず点数不変。架空の改善点や初回案の再構成はない。B-1相対点AWS64/GCP62/Azure59は使用していない。

|合格条件|I|F|R|
|---|---|---|---|
|80点以上|否：66|否：66|否：66|
|全項目3以上|適|適|適|
|要件理解/Architecture/Security/Availability/Cost/DRが4以上|否：要件理解だけ4|同左|同左|
|設計合否|不合格|不合格|不合格|

これはAI自己評価。工程完了・設計合格・最終選定・人間採用承認は独立。AWS優先参考設計/選定保留、人間採点・採用承認未取得、C移行保留。次工程はB-2限定差戻し。
