# C-0実行記録

2026-09-10（Asia/Tokyo）。対象は移行条件・限定実験・承認票の整理とGitHub PR反映だけ。取得可能な操作と判断理由を記録し、非公開の内部思考は保存しない。

## 起点・PR確認

GitHub connectorで取得した状態。base SHAはPR API応答の比較基準値であり、現在のbranch tipとは区別する。

|PR|state / merged|現在head / SHA|base / API base SHA|
|---|---|---|---|
|#12|closed / true|b2/cloud-selection-design / 2e04272067a9c965d5a03614eb1594c09ae43a25|main / ce6a1be764c7e46a233598618ef9a1baf9e5d2cd|
|#13|closed / true|b3/evaluation-handoff / 2e04272067a9c965d5a03614eb1594c09ae43a25|b2/cloud-selection-design / cbcc26dc4d6f471e0934bb5fac7200411a038321|
|#14|closed / true|reports/b3-developer-summary / 2e04272067a9c965d5a03614eb1594c09ae43a25|b3/evaluation-handoff / 337188536c4268da4b8450f7ac02729f809e1b66|

ローカル取得mainは`6bd48f162d027da0056112cac45f08f52d54e903`。merge履歴#12=`3a56584aab694327a99ae112766dbeed1160ba4d`、#13=`c1f5f1cb753be175c31690dc79b160b7165f847c`、#14=`c32b8a1f48b680c0c837649ec4b1d1deaa8f0e5c`を確認。#14 headから起点への`merge-base --is-ancestor`成功、`diff --name-only`のB-2/B-3差分なし。後続mainの説明更新も継承するためこの起点を選択。mainだけを根拠に最新と判断していない。

branch `c0/transition-readiness`、PR比較先`main`。#14→#13→#12の依存は統合済み、未マージの依存PRなし。履歴の採点SHAを現在headで上書きしない。今回マージしない。

## 確認資料と実施内容

依頼されたB README/final-report、B-3 baseline/review/scores/revised-design/traceability/c-validation-plan/c-cost-model、正式業務回答、A-1 requirements、execution-policy、rubric、handoff、resource-inventory、Issue #9を確認。追加は参照されたB-2 design/recovery-observability/selection/cost/validation-planの必要節と正式補足のC/合格条件。長いファイルは必要節/検索で確認した。

公開資料の新規単価/仕様調査、再設計、採点や既存試験のやり直しは行わず、既存根拠を引用。費用は既存JSONから参考内訳を再計算し、最新価格・実行可能な上限とはしない。C-0承認票の確定不能項目は要回答・全欄未承認とした。

実行操作：GitHub PR/Issue読取り、対象repo clone、git履歴/祖先/差分確認、C-0文書と導線/引継ぎ/台帳の限定編集、文書検査、commit/push/PR作成・反映確認。GitHub Issue #9は技術未解決を維持して関連付ける。

環境記録：通常cloneはネットワーク制限で失敗、承認付きcloneで取得。ローカルgitは所有者差に対し当該repo限定の`-c safe.directory=...`を使用。gh CLIなし、GitHub connectorを使用。connectorの一部引数形式不一致は修正して再取得。ユーザーからクレジット中断後の続行指示を受け、同じC-0範囲で再開。利用枠のリセット/購入はしていない。

公開物に秘密/個人情報/State/Plan/実accountや宛先を含めない。非公開の承認対象値は公開リポジトリへ転記しない。今回クラウド操作/故障/負荷/メールなし、既存アカウント資源と請求は未確認。指定名GPT-6 Astra Lightは既存条件、実モデル識別・トークン使用量/残量・モデル料金・実作業時間は取得不能で不明。時刻差を実作業時間にしない。

## 検査・リモート反映

文書検査：C-0文書と本記録の相対リンクの参照先欠落0、対応表のT01〜T16欠落0、既存JSON再計算12,495円/50%参考18,742円で一致。変更文書の秘密鍵/APIキー/メールアドレス形式の検索で該当なし（完全な機密不存在の機械保証ではなく、内容も確認）。`git diff --check`問題なし。設計/コード変更がないためクラウド/実装試験は実施しない。

変更SHA・PRとリモート照合結果は反映確認後に追記する。C-0整理完了と承認取得を混同せず、次工程には進まない。
