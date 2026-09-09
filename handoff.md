# 再開情報

更新2026-09-09。A-1/A-2/A-3工程完了（A-3 GitHub反映を最終確認）。A設計は初回61・修正後65点で合格条件未達。採用承認保留、PRマージなし、B未着手。
保存先PUBLIC：https://github.com/moruku36/cloud-validation-level3-astra-light 。再確認不要。
ブランチa3/aws-review、base origin/a2/aws-design=b5f5022e4475499661e0c41e2a60eeb91a0364d5。PR #5未マージ、mainを基準にしない。初回81cab82、レビュー前b5f5022を履歴/experiments/A/A-3/baselineへ保存。最新commitはgit rev-parse HEADで確認。

## 現在の判断
A-2候補の基盤選択/台数は維持、採用承認なし。A-3/revised-design.md・budget.mdが旧仕様/費用の修正優先文書。
監視費を月166.44USD追加して小計667.54USD＝110,144円、予備20%込132,173円。為替150と税10%は仮定。REQ-12未達、価格/保持量/容量に未確定。
復旧は影響発生から検知・回復・実時間300秒安定まで。毎分5回だけでは不十分として修正。片AZ性能/全認証DNS経路/DB再接続は未実測。国内保存/受信メール/退会台帳/期限消去に未確認。
Issue #4は根拠付き文書訂正のみ解決、実現性はOPEN維持。
人間採点空欄。指定モデルGPT-6 Astra Light、実行モデル識別/実残りトークン数は未取得。

## 次回
人間の判断を待つ。予算増額か監視/基盤の再設計、削除台帳/メール国内保存範囲、未保証の復旧依存/運用体制を判断。Bの開始は明示指示がある場合だけ。今回はB未実施。
読む順：本ファイル、resource-inventory.md、A-3/review.md・scores.md・budget.md・validation-handoff.md。必要対象だけ追加読込。公式主要単価の再調査を繰り返さない。
必要コマンド：git status --short、git rev-parse HEAD、git ls-remote origin a3/aws-review、gh pr view（A-3番号）--json baseRefName,headRefOid,state（base a2/aws-design・OPEN）、gh issue view 4 --json body,state（OPEN）。
今後CはC-0の予算/許可/期限が先。試験T01〜11は未実施、法令適合完了ではない。

## 資源・承認
クラウド操作なし、本実験残存なし、実クラウド費0円、削除期限なし。既存アカウント全体未調査、モデル利用費未取得。
今回承認はA-3レビュー・限定設計修正・公開成果物/PR/Issue更新。採用承認、merge、資源作成、B開始は承認されていない。workflow権限はC前の課題で今回変更なし。
