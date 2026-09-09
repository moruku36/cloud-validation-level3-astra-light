# B-1 実行記録

実行日：2026-09-09。目的は曖昧な正式業務要件からの3クラウド同条件比較。公開資料/合成シナリオのみ、内部の非公開思考・実PII・secret・State/Planは保存しない。完全な逐語会話/操作ログではなく、取得できた操作と判断根拠の要約である。

## 入力と承認

今回の添付指示を入力とした。B-1開始・AWS/Azure/GCP各1案・基準事前コミット・比較/概算/相対順位/必須判定/暫定判断/未確認・Issue/README/handoff/台帳・commit/push/PR/remote本文確認まで承認。サブエージェント、クラウドリソース作成/環境変更、PR merge、B-2最終選定・詳細設計、B-3正式評価、C実装は禁止。
優先入力：[正式業務回答](../docs/sources/business-answers-2026-09-08.md)、[24要件](../experiments/A/A-1/requirements.md)、[実行方針](../docs/execution-policy.md)、[rubric](rubric.md)、[正式補足](../docs/sources/supplement-2026-09-08.md)。A完了報告・最終レポートの仮定/残課題を引継ぎ、A製品を必須化しない。

## モデル/計測情報

|項目|取得結果|
|---|---|
|ユーザー指定モデル名|GPT-6 Astra Light|
|実行モデルの識別情報/設定|未確認。指定名を実測値として扱わない|
|トークン使用量/残量・モデル料金|不明。推測/計算で補わない|
|実行時間・レビュー修正時間|不明。コマンド個別wall timeを工程全体へ足し上げない|
|サブエージェント|使用なし|
|この実行中の追加業務回答/設計ヒント|0件。初回添付の共通条件/配点/保存先を使用|
|クラウド操作|なし。公開価格API/公式WebのGETのみ。実アカウント/請求は未確認|

## 開始時の確認と順序

1. 添付の依頼文を範囲読取り。GitHub PR #8を確認：OPEN/merged=false、head reports/a-completion、SHA 8f427118c7a6522817d1fd7d0842d4aec7f4023c、base main SHA 2a97796c7429e3f968a35997d9b6a53257eb84cb。
2. #8 headをclone、b1/cloud-comparisonを作成。比較先reports/a-completion、#8依存。Issue #4はAPIでCLOSEDを確認。過去文書のOPEN/未マージを現在状態にしない。
3. handoff/台帳/A完了/実行方針/正式回答/24要件/rubric/補足/A最終の必要範囲のみ確認。既存A価格抽出を再利用。
4. [comparison-criteria.md](../experiments/B/B-1/comparison-criteria.md)を **4f486d2** に単独コミット。候補比較/採点より先。100点の重みと尺度は以後不変。
5. 重要仕様/価格だけ公式に追加照会：Azure公開meter、Container Apps/DB HA、Cloud Run/SQL/backup/Armor、Lambda/SES等。検索に混在した第三者情報を価格確認根拠にしない。SKU未照合はEとした。
6. [comparison](../experiments/B/B-1/comparison.md)、[cost](../experiments/B/B-1/cost.md)、[sources](../experiments/B/B-1/sources.md)、cost-model.json/azure-rates.jsonを作成。初回相対採点は64/59/62（AWS/Azure/GCP）。B-3採点なし。
7. 未解決7論点を[Issue #9](https://github.com/moruku36/cloud-validation-level3-astra-light/issues/9)にOPENで作成し#4継承を明記。README/handoff/台帳を更新し、remote照合後に完了記録を追記する。

## 判断と修正履歴

|項目|判断/修正と理由|
|---|---|
|AWSの再判断|既存ECS/RDSを性能の正解とせず、SQL transaction/移植性/managed運用を比較理由に採用。authは国内framework、monitorは同粒度の独自probeへ変更。人件費を除外しても負担を採点|
|外向き200GB|正式回答の総量に戻し、Aの画像200＋API56.7の二重加算を継承しない。候補採点前の基準で訂正|
|DB地域copy|事前仮定30GB/月は日次全dumpで不足。全社20GB×30=600GBへ同じように修正。初回基準を保存し、重み不変|
|GCP PITR|共通仮定30日にはPlus。業務必須ではないことと、全社7日に揃える再比較で概算が変わる感度を明記。東京価格は未確認の係数計算|
|費用精度|V/E/Uを分離。見積不能費を0円と認定しない。Azureの確認済み固定費超過、AWS/GCP未確認を別判定|
|外部依存|AWS Tokyo SES/東京大阪probeを全社共通化。Azure/GCPにAWS契約/監視/IAM負担が加わる点を明示|
|最終選定|全案に重要未確認。AWSを次の検討優先とするのみ。B-2に進まない|

候補初回本文は最初の候補コミットで保存、後の訂正は追加コミットにする。基準・A成果物・初回案を上書きで失わない。

## エラー/再試行・公開確認

- gh未導入。GitHubコネクタ＋gitを使用した。
- 初回git cloneはsandbox networkで接続失敗。指定repoの取得目的で承認review経由のnetwork実行に成功。
- cloneの所有者相違によるdubious ownershipはrepo限定git -c safe.directoryで対応。global設定を変更していない。
- WebのCloud SQL料金等取得は複数回エラー。公開HTMLの直接GETは成功したが、東京SKUの最終照合は未完。大きいHTMLをtext変換した際にscript/styleの長行が残り出力が切詰められたため、以後全文/長行出力を避けた。価格を確認済みに格上げしない。
- Azure WAFはskuNameがStandardで、productNameにWAF v2がある。初回フィルタで表示0件となりproductNameで必要meterを抽出。Discountedを選ばない。対象3応答のNextPageLink=nullを確認（16/140/23件）。
- PowerShellのforeach結果を直接pipeする構文エラーを1回修正。保存/環境変更への影響なし。
- GitHub Issue作成の最初の試行は自動承認reviewで「構成/費用等の公開許可が未確認」と拒否。別手段で迂回せず、get_repoでpublic/adminと指定repoを確認し、fetch_fileで公開済み正式回答が架空検証シナリオであることを確認した。その根拠と今回の公開保存承認を明示して同じコネクタで再試行しIssue #9作成成功。
- GitHub tool引数のrepo/repository_full_name不一致を修正。schemaエラーは外部変更成功として数えない。
- Git authorは汎用Codex/noreplyを使用。公開文書は架空業務条件、公式単価、repo/commit参照のみ。個人ファイルパス・認証token・機密State/Planは保存しない。

## 検証・GitHub完了証跡

候補コミット後に計算式/24ID/配点/相対リンク/公開差分を点検し、訂正とremote確認を次の追記で記録する。実アプリ試験、クラウドCLI、apply、mergeは未実施。

### 初回案保存後の点検

- 初回案保存commit：1812e6d。AWS/GCP/Azure相対点64/62/59は変更なし。基準4f486d2も変更なし。
- cost-model.json全行再加算：AWS460.8123635/Azure1312.0770146/GCP821.6966146 USD、税込76,034/216,493/135,580円、20%参考91,241/259,791/162,696円。本文の表示と一致。
- 比較表REQ-01〜24を24行確認。配点合計100、加重点計算を確認。対象8文書の相対リンク存在確認とgit diff --checkに合格。
- 保存候補の秘密鍵/token形式/ローカル個人pathの簡易検索は該当なし。完全なDLP審査や実cloud適合を意味しない。
- AのS3公式抽出は東京のみのため、大阪DB dump storage行のV表示をE（東京単価代用）へ訂正。金額は変更なし、初回を1812e6dに保持。
- Azure内部ACA/WAFとGCP regional外部ALB/Run/Armorの接続関係に公式根拠を追加。詳細設定/課金/性能は未確認のまま。
- READMEのB保留表示をB-1成果物へ更新。Aの構成/金額は履歴として保存し、今回比較に必須化しない。

### GitHub反映完了

比較本文の最終内容commit：b81b2bdca180f3f28e456201f9c17a075185272c。push成功、[PR #10](https://github.com/moruku36/cloud-validation-level3-astra-light/pull/10)を作成。head b1/cloud-comparison / base reports/a-completion (8f427118c7a6522817d1fd7d0842d4aec7f4023c)。PR #8依存を本文に明記。#8/#10は再取得時OPEN/merged=false/mergeable=trueで、今回mergeなし。

指定8主要文書をGitHub fetch_fileで読み戻し、返されたblob SHAをlocal git ls-treeと比較して全一致。特にcriteria 5b385aaa / comparison 51296cf7 / cost bd6a1633 / sources 9f823e7a。Issue #9にPR #10を関連付けるコメント（id 5600618200）を追加、未解決の7項目をOPEN維持。コネクタのコメント引数名差異はschemaエラー後に修正して成功。

この完了記録・README・handoffの追記を最終追跡commitとしてpushし、最終head/SHAと変更文書のremote blobを再照合する。最終SHAは自己参照で書込まずPRのhead/終了報告で解決する。完了工程はB-1のみ、B-2/B-3/C未実施。新しいcloud資源/実費/削除期限なし（台帳/アカウント未確認の区別を維持）。
