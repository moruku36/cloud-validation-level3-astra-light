# B-2実行記録（採点ではない）

日付2026-09-10。指定モデルGPT-6 Astra Light、実際の識別情報は未確認。モデル料金・トークン使用量/残量・全実行時間は不明。サブエージェント不使用。非公開内部思考は保存せず、入力・外部操作・判断理由・修正だけを記録する。

## 入力と再開確認

- 添付のB-2限定指示・正式業務回答・24要件・B-1 README/比較基準/比較/費用JSON/出典、handoff/resource-inventory/execution-policy、rubric/正式補足を必要箇所だけ読んだ。
- GitHub PR情報を取得し#8/#10/#11がmerged=trueを確認。最新mainは4afc6cc4b7c1d1bf9ceb05b2e0aff8e958734210、#11の統合commitと一致。B-1原成果物7c06ed0432a86b6a3c23db4eb85872d0e4591192を保持。
- mainからb2/cloud-selection-designを作成。比較先main、未マージ前工程依存なし。Issue #9 OPENを確認、過去PR本文の未マージ表現は履歴として扱った。
- 共有会話URLはCache miss。添付/正式資料を根拠に継承した。memory索引にはLEVEL3/B-1/B-2の関連hitなし、過去memoryの事実を設計根拠にしていない。

## 操作・失敗・判断

1. read-only cloneはsandboxのnetwork制約で失敗、承認されたnetwork実行でclone成功。ローカルghなし。GitHub connectorとgitで作業。checkout所有者差によるsafe.directoryは当該checkout限定のgit -cで処理しglobal設定を変更しない。
2. GCP公式SQL web取得は容量上限で失敗。公式HTMLの静的JSON dataから東京edition別単価を抽出して解決。LBの内部0.008と外部東京0.012を区別して訂正。外部ページscriptは実行していない。
3. PITR最低7日を3社共通の未承認条件案にした。GCP Plus固定を外す一方、backup量を勝手に日数比例で減らさなかった。
4. AWS非本番入口を常設として保守負担と課金の整合を改善。共通監視/DR資材を全案に加算。費用の全行式はB-2 cost-model.jsonへ保存。
5. 国内保存範囲について受信者メールサービス側も対象かを質問した。未回答を承認と扱わず条件別判断を記録。全案の重要未確認から最終選定保留、AWSは優先参考設計にとどめた。
6. 初回案をレビュー修正前に独立commitする。以後は追加commitで履歴を維持し、A/B-1成果物・採点を変更しない。

## 初回案の状態

[B-2 README](../experiments/B/B-2/README.md)から8必須文書、構成図、費用JSON/公式抽出へ到達する。24要件の実証対応を作成。選定保留・人間採点空欄・設計合格未判定。復旧配分/保持/工数は設計仮定で実測ではない。

## 検証・remote反映

初回commit後、費用再加算/感度・相対リンク・24要件・diagram/secret混入・禁止ファイル変更を点検し、結果を追記する。必要な修正は別commit。最終GitHub反映・PR head/base/依存・remote本文照合の結果は後続の完了欄へ記録する。未反映段階ではB-2完了としない。

今回クラウド操作/IaC/app/CI-CD実装実行/PR mergeなし。作成/削除/期限の新規対象なし。台帳上の実験残存なし/実費0円を引継ぐが、アカウント全体・請求書は未確認。次は別途明示指示によるB-3、Cへ自動移行しない。

## 初回保存後の点検・修正

初回commit `7daa93c`を保持。24要件表の欠落なし、11 Markdownの相対リンク欠損なし、AWS26/GCP25/Azure24費目を再加算し税込/20%参考/差分の一致を確認。結果はAWS83,248/99,898、GCP101,933/122,320、Azure218,588/262,306円（U別）。秘密情報の典型パターンを点検し該当なし。

設計点検でGCPへ逆転した際の配置/ingress/IAM対応を追記。削除台帳だけでなくDB内outbox断片がrestoreで戻る場合の元期限継承を明文化した。root README/handoff/resource-inventoryの現在状態をB-2へ更新し、A/B-1本文・採点・初回案は変更していない。これはB-2文書点検でありB-3正式評価ではない。構成図は編集可能Mermaidソースとして参照・node/edge構造を点検、実機配置や画像renderの検証ではない。

## GitHub反映の完了記録

初回`7daa93c`→点検修正`6b330dc1ac91829f013ecf441bc4468034505e3c`をpush、[PR #12](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/12)を作成。`6b330dc`を指定して14成果物の本文をGitHubから取得し、すべてlocal blob SHAと一致確認。内訳はB-2の8必須文書＋2 JSON、run、root README/handoff/resource-inventory。Issue #9は7論点全体を未チェックで維持し、B-2結果を冒頭へ追記した。

作業中mainに`ce6a1be764c7e46a233598618ef9a1baf9e5d2cd`のB-1図表追加を検出。変更3文書の差分を読み、正式要件・cost-model・採点は変わらないことを確認。`a3a58a457c62973e8548ae1005d415e1e84c1311`で作業branchへ取り込んだ。B-2 PR差分にはA/B-1変更がない。追加図の削除/匿名性に関する表現を新規要件・確認済み根拠にしない。

比較先はmain、未マージ前工程依存なし、PRはOPEN/未マージで停止。完了記録を含む最終headはPR commit一覧と終了報告で解決し、push後に変更した追跡文書本文・head/baseを再取得する。B-2工程完了・最終選定保留、設計合格/人間採用は未承認。次は明示指示後のB-3のみ。
