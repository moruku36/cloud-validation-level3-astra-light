# LEVEL3-B 詳細レポート：比較・選定設計・評価引継ぎ

2026-09-10。**Bの文書工程完了と設計採用は別である。B-3自己評価66点、設計不合格、AWS優先参考設計・最終選定保留、人間採用承認未取得、C移行保留。** GitHub反映確認は[実行記録](../../evaluation/B-3-run.md)。次工程はB-2限定差戻しで、C-0を自動開始しない。本書はA詳細レポートでもB-1単独サマリーでもなく、B全体の追跡可能な評価記録である。

## 目的・入力・範囲

曖昧な業務シナリオを正式回答に基づく要件へ固定したうえで、3社を同じ条件で比較し、合理的な構成を選定・設計できるか評価した。正式入力は[業務回答Q01〜Q08](../../docs/sources/business-answers-2026-09-08.md)、[24要件](../A/A-1/requirements.md)、[正式補足](../../docs/sources/supplement-2026-09-08.md)、[rubric](../../evaluation/rubric.md)。今回のB-3指示を工程範囲の最優先とし、正式業務条件/配点/合格基準は変更していない。

初期は登録1万人、100万PV/月、API通常10/peak100RPS15分、同時利用500人、read/write9:1。主要API p95≤500ms・server error<1%、本番DB20GB/画像100GB、月増分2/10GB、転送200GB。税込初期本番＋最小非本番10万円、国内保存/外部依存確認、退会30日以内稼働系削除/backup35日上限/復元再削除。開発5人・専任1人、夜間即応保証なし。1000RPS・登録100万人・将来予算は分離する。

指定モデルはGPT-6 Astra Light。実モデル識別情報は未確認。トークン使用量/残量、モデル料金、実作業時間は取得できず不明。コミット時刻差で時間を推測していない。サブエージェント不使用。B-3は文書レビュー・最小限の公式根拠確認・限定訂正・採点・計画・GitHub保存のみ。クラウド操作、IaC/app/CI実装実行、PR merge、C-0/C開始、人間採点/採用/予算承認の代行はない。

## 履歴・比較方法

|工程|固定commit/PR|成果物・意味|
|---|---|---|
|B-1事前基準|4f486d2e1d2cf82fbb0571e440d31b7841a0580e|[criteria](B-1/comparison-criteria.md)。採点前に共通条件/重み/尺度を記録|
|B-1初回/完了|1812e6dc33d254be868b25b487ed962053a7f0d0 / 7c06ed0432a86b6a3c23db4eb85872d0e4591192、[PR #10](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/10)|[B-1](B-1/README.md)。相対点AWS64/GCP62/Azure59は正式合否でない|
|B-1説明整理/後付け図|[PR #11](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/11)、図ce6a1be764c7e46a233598618ef9a1baf9e5d2cd|説明用。比較の事前条件・正式要件を上書きしない|
|B-2初回|7daa93c08be4508632af5d4669702a5bccb5bd67|[初回実物](https://github.com/moruku36/cloud-validation-level3-astra-light/tree/7daa93c08be4508632af5d4669702a5bccb5bd67/experiments/B/B-2)。再構成ではない|
|B-2完了/B-3起点|cbcc26dc4d6f471e0934bb5fac7200411a038321、[PR #12](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/12)未マージ|[B-2](B-2/README.md)。最新headとgit一致を確認|
|B-3固定/限定修正|baseline独立commit9047d62、R c0cf660d14af3ed67559a1d8d0244ddf4f164fd7|[baseline](B-3/baseline.md)、[限定修正](B-3/revised-design.md)。最終PR/headは[handoff](../../handoff.md)|

3社に同一業務負荷/データ量/国内保存/復旧/非本番/監視/メールを適用し、税10%・150円/USD、無料枠/credit/長期割引を使わず比較した。通常負荷継続時間/peak頻度/ログ量/内製工数はAIの計算仮定として区別。AのAWS指定はBの選定条件にしていない。B-2 SKU変更による比較は条件付きであり、安いSKUの性能を旧SKU相当と断定しない。詳しい方法と出典はB-1文書を再利用し、重要差分だけ[review](B-3/review.md)で確認した。

## 3案と採否・変化

|案|代表構成・理由|B-1→B-2/B-3基本税込月額|保留/不採用理由・逆転条件|
|---|---|---|---|
|AWS|Fargate ARM2AZ＋RDS PG Multi-AZ＋ALB/WAF、SQL auth/outbox、SES、国内2地域監視/DR|76,034→83,248円＋U|最安既知基本費で参考優先。保存/削除/無人復旧/容量/内製体制未確定。必要費が上がれば順位再検討|
|GCP|Cloud Run＋Cloud SQL Enterprise HA、代替ingress/IAM、同じ業務条件|135,580→101,933円＋U|PlusからEnterpriseへ条件付き変更しても基本予算超過。性能/経路/費用を同条件で満たせれば逆転候補|
|Azure|managed container＋PostgreSQL HAを中心とする代表案|216,493→218,588円＋U|大幅予算超過。要件維持の別価格構成を裏付けられる場合のみ再比較|

AWS差7,214.33円は非本番入口常設化＋監視＋DR資材。GCPはDB差−217.54USDとTokyo LB補正等、Azureは監視/DR増。算術再計算一致。AWS残余16,751.63円はU/必要増強で消費される。20%参考額99,898円を「精算済みで10万円適合」と扱わない。本番・非本番・外部依存の重複計上は今回検出なし、実meter/適用未確認は残した。[費用レビュー](B-3/review.md)と[B-2内訳](B-2/cost.md)を正とする。人件費除外はauth/monitor保守負担を無視する理由ではない。

I→FはGCP経路/IAMと退会outbox原期限の説明を追加した2段落。B-3ではB-2原文を変更せず、S3複製先削除/失敗処理、RDS0–35日訂正、Route53query log所在地、管理画像role差戻し、KMScleanup例外を補足。予算・業務要件・全体構成の改変はない。

## 評価・誤り・未解決

|評価版|自己評価|設計判定|人間評価|
|---|---:|---|---|
|初回I|66/100|不合格||
|B-2完了F|66/100|不合格||
|B-3限定修正後R|66/100|不合格||

配点別根拠・固定SHA・算式は[scores](B-3/scores.md)。全項目3以上だが80点未満、必須6項目中Architecture/Security/Availability/Cost/DRが3で条件未達。正直な選定保留を隠蔽として減点していない。説明の限定訂正だけで重要根拠不足が解消したと見なさず点数不変。人間評価/採用承認は空欄・未取得。

発見した明確な誤記はRDS instance保持可能範囲。S3/Lifecycle/replicationとDNS/KMSは説明不足/見落とし得る条件を公式根拠で補足した。既知算術誤りはなし。指摘→原状態→変更→結果→採点影響を[revised-design](B-3/revised-design.md)、未解決F01〜F11を[review](B-3/review.md)で追える。

H人間判断：メール受信側の保存範囲、PITR最低期間（7日案未承認）、auth/probe保守の主副担当/工数、救済不能な正常更新の受容。D設計差戻し：全copyの原期限/再削除、admin image IAM、全依存無人復旧/片AZ容量、監査/保存経路、必要容量込み予算、論理破損救済。E実証待ち：T01〜T16。追跡は[Issue #9](https://github.com/moruku36/cloud-validation-level3-astra-light/issues/9)、旧#4のclosedを技術解決としない。工程完了を理由に未解決Issueを閉じない。

取得可能な人間の介入は[human-intervention](../../evaluation/human-intervention.md)。初期工程依頼は補足回答回数に含めず、B-2完了報告はGitHubで照合してから利用。未回答を承認にしない。過去累計3回答は既存記録の範囲に限り、取得不能な会話の介入・時間は推測しない。

## 証拠の限界

実際に確認したのはGitHub状態/履歴/初回文書の存在、比較条件の追跡、費用/採点算術、限定公式仕様、24要件/リンク/公開対象である。配置、暗号化、削除、backup/PITR、正常更新救済、監視、RTO/RPO、性能は設計根拠または計画であり実証なし。実アカウント全体/請求未確認、台帳上残存なし・クラウド実費0円を継承したにすぎない。モデル料金等は別途不明。

RTOは影響発生から検知を含め実時間300秒安定終了まで30分。RPOは障害時刻と復旧最新確定data時刻の差5分。SLA/典型的failover時間をE2E保証へ置換しない。月間99.9%は短期試験で証明不可。論理破損4hは判断からの暫定目標で、発見遅延と救済不能損失を別記する。region停止へ30分/5分を流用しない。法令適合確認は技術レビューだけで完了しない。

## Cへの引継ぎ

[C計画](B-3/c-validation-plan.md)に本番/L/H差分、工程別前提/操作/要件試験/合否証跡/時間/費用/cleanup/中断再開を記録。小型単一AZで機能を確認し、本番相当Hでのみ性能・片AZ・DB障害・20GB論理復元を評価する。1000RPS/DB障害/費用2倍/publicIP禁止は同一baselineから独立させる。C-0〜C-10は1回1工程、今は開始しない。

短期基本計画12,495円＋U、50%参考18,742円＋Uは未承認。長期保持実時間試験/暦月SLOは別枠。費用が安い試験構成を本番性能の証明として扱わない。試験前後/終了時に残存確認、証跡後削除、日跨ぎ課金資源は原則削除/再構築。disk/IP/LB/NAT/DB/backup/log/鍵等を点検し、削除確認前にState/復旧情報を失わない。KMS待機など例外は事前承認・期限確認が必要。

結論を分離する：B-3文書/評価/引継ぎはGitHub確認により工程完了、設計は不合格、最終選定は保留、AWSは参考優先、人間採用承認は未取得。次の1工程は**B-2限定差戻し**。Hの判断とDの設計根拠補完後に再評価し、設計承認・未解決の扱い・別実験予算・操作許可・保持期限の各条件が整うまでC移行保留。
