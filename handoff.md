# 再開情報

更新：2026-09-08（JST）。

## 完了工程・版・GitHub
A-1要件整理完了。Q01〜Q08に正式な実験業務回答を反映、重大業務不足なし。設計・環境の要件適合は未判定。A-2未着手。
PUBLIC保存先：https://github.com/moruku36/cloud-validation-level3-astra-light 。公開範囲確認済み。
ブランチ：a1/requirements。初回案6731042、回答待ち保存1a0c766。正式回答反映版は本ブランチの今回完了コミット。
現在のコミット：git rev-parse HEADで取得。本ファイル自体のハッシュを自己埋込しない。
PR #3：https://github.com/moruku36/cloud-validation-level3-astra-light/pull/3 （OPEN・未マージ、base prep/requirements-intake）。準備PR #1も未マージ。
回答Issue #2は回答反映をremote確認後に完了クローズ。未解決のA-2評価事項：https://github.com/moruku36/cloud-validation-level3-astra-light/issues/4 。

## 確定事項・仮定
AのみAWS、Bは同条件3社比較。正式補足と正式業務回答が取得できない原本部分を補完。原本再提示不要。
実験条件：動的10/100RPS・ピーク15分・500人、p95≦500ms・エラー<1%、主要機能暦月99.9%。単一AZまでRTO30分（影響開始〜復旧後5分安定終了）/RPO5分。論理破損4時間暫定、地域停止は別。
本番データ/backup国内、退会稼働系30日削除/backup上限35日/復元後再削除。初期本番＋最小開発検証税込10万円、必須費用込み。日中対応のみで夜間即応を前提にしない。
残る仮定：月間負荷継続率・メール/ログ/静的要求量・測定粒度・非本番数等はA-2で明示。100万人と要求100倍を混同しない。将来予算未確定。
指定モデルGPT-6 Astra Light、実行モデル識別未確認。実残りトークン数は取得していない。

## 次回の1工程
次回はA-2のみ。ユーザーの明示実行指示を待つ。今回A-2を自動開始しない。
開始時は本ファイル、resource-inventory.md、experiments/A/A-1/requirements.md、assumptions-risks.mdを読み、必要時のみ正式回答と共通指示を読む。
最大3案のAWS設計比較、構成図・採否理由・リスク・初期費用を作成。公式仕様/単価は判断に必要なものだけ出典・確認日付きで確認。資源作成なし。A-3には進まない。
Issue #4を使い、実現性リスクを評価。不成立は根拠・超過・調整案として提示し、無断緩和しない。

## コマンド・期待結果
- git status --short / git rev-parse HEAD / git ls-remote origin a1/requirements：クリーン・remote一致。
- gh pr view 3 --repo moruku36/cloud-validation-level3-astra-light --json state,headRefOid：OPEN・head一致。mergeしない。
- gh issue view 2 / 4 --repo moruku36/cloud-validation-level3-astra-light --json state：回答2はCLOSED、後続4はOPEN。
- A-2開始時は現在ブランチから新ブランチを作成し、未マージPR #3をbaseとする積み重ねPRか、最新状態に合わせた非破壊手順を選ぶ。完了済み回答を再質問しない。

## 残存・費用・許可
今回クラウド操作なし。本実験作成残存なし、クラウド費用0円、削除対象/期限なし。既存アカウント全体未調査。モデル等費用未取得。
将来費用未算定。C実験上限/期限/許可/保持はC-0で別途確定。
今回承認：A-1回答反映、公開保存、PR/Issue更新、次回A-2の再開情報。今回未承認：A-2実行・資源作成・マージ。
workflow空ファイルは権限不足でGitHub対象外、CのCI/CD工程で権限を確認。今回権限拡張なし。
