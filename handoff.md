# 再開情報

更新：2026-09-08（JST）。

## 完了工程・現在地
正式補足統合・準備の阻害解消をfb86c543b826003f44bf669215327a1e13d62a24でGitHub保存確認してからA-1開始。
A-1初回要件整理は作成済みだが重要回答待ちで未完了。A-2以降未着手。
公開保存先：https://github.com/moruku36/cloud-validation-level3-astra-light （PUBLIC指定済み、再確認不要）。
準備PR：https://github.com/moruku36/cloud-validation-level3-astra-light/pull/1 （未マージ）。
ブランチ：a1/requirements。基点：prep/requirements-intake のfb86c54。A-1 PR・初回コミットは作成後追記。
現在コミットは本ファイルを含むブランチ先端（git rev-parse HEAD）。
未解決：https://github.com/moruku36/cloud-validation-level3-astra-light/issues/2 。

## 確定事項・仮定
AはAWSのみ、BはAWS/Azure/GCPを同一条件で再選定。未取得原本は未取得のまま、正式補足が不足を補完済み。原本再要求は不要。
初期シナリオ・配点・合格基準・共通指示を統合。要件値を緩和していない。
平均換算例のみ30日/月。ピーク、障害範囲、予算包含範囲の合意済み仮定は置かない。機能・性能・SLO/DR・データ・予算・運用のQ01〜Q08待ち。
指定モデルGPT-6 Astra Light、実行モデル識別は未確認。取得可能な実残りトークン数なし。

## 次回の1工程
A-1継続のみ。ユーザー回答をquestions.mdへ記録し、要件表・仮定・リスク・Issueを更新。通常回答と設計誘導を分離して介入回数を更新する。
重要未回答は回答待ちを維持。全重要条件が解消または明示合意された場合のみA-1完了判定。A-2は別の明示指示が必要。
最初に本ファイル、resource-inventory.md、experiments/A/A-1/questions.md、requirements.mdを読み、変更対象だけ追加で読む。

## 必要コマンド・期待結果
- git status --short、git rev-parse HEAD、git ls-remote origin a1/requirements：作業状態とremote一致確認。
- gh pr view（A-1のPR番号） --repo moruku36/cloud-validation-level3-astra-light --json state,headRefOid,url：OPENとhead一致。
- Q01〜Q08の回答と要件ID/受入条件を照合し、未定の合格値や未実施試験成功がないことを確認。
- git diff --check、公開情報とリンク検査後コミット・push。Issue/PR相互参照を更新。マージしない。

## リソース・費用・承認範囲
今回クラウド作成・課金操作なし。残存（本実験作成分）なし、今回クラウド費用0円、削除対象/期限なし。アカウント全体の既存資源は未調査。
本番初期上限10万円/月、包含費目待ち。将来費用未算定。実験の全体/工程予算・許可・保持はC前に確定。モデル等利用費未取得。
承認：公開GitHub保存・PR・Issue作成、A-1要件整理。未承認：マージ、詳細設計への移行、クラウド作成・破壊操作。
.github/workflows/空ファイルは既存認証のworkflow権限不足で公開対象外。実装工程で対応、今回権限変更なし。
