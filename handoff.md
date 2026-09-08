# 再開情報

更新：2026-09-08（JST）。

## 現在地
- 保存先作成完了：https://github.com/moruku36/cloud-validation-level3-astra-light 。PUBLIC、ユーザー承認済み。再確認不要。
- 準備は原本の不足部分により未完了。A-1未着手。A-2以降未着手。
- 作業ブランチ：prep/requirements-intake。基準コミット：8d5b060。PRは作成後追記。
- 最新コミットは本ファイルを含むブランチ先端（git rev-parse HEADで取得）。自身のハッシュを自身に埋め込まない。

## 確定事項・仮定
共通指示と初期シナリオを適用。共有チャットの表示本文を保存。詳細はdocs/requirements.md。
単一クラウドは未指定。共有チャットのAWSは例示であり指定とみなさない。
指定モデルGPT-6 Astra Light、実行モデル識別は未確認。業務仮定は未設定。

## 未完了・阻害要因
- 共有チャットでは追加文書本文・評価配点が表示されない。ユーザーから本文またはファイルを受領して照合する。
- Aの単一クラウド指定が必要。
- 前工程の不足原本の反映が完了するまでA-1の依存作業に進まない。

## 次回の1工程
A-1。前提：不足原本受領→準備文書更新→GitHub反映を確認。続いて単一クラウドを確認し、要件整理のみ。A-2へ進まない。
開始時は本ファイル、resource-inventory.md、docs/requirements.mdを読む。原本全文・過去ログの不要な再読はしない。

## コマンド・期待結果
- gh repo view moruku36/cloud-validation-level3-astra-light --json visibility,url → PUBLIC・指定URL。
- git status --short → 作業状態確認。git rev-parse HEAD / git ls-remote origin prep/requirements-intake → 同一コミット。
- gh pr view --json url,state,headRefOid → PRがOPEN、意図したブランチ先端。
- 不足文書照合後、確定事項・質問・仮定・制約・矛盾、可用性の測定条件・対象障害・RTO/RPO・負荷・予算、要件ID・受入条件を作成。人間の回答と誘導を分離記録。

## リソース・費用・承認
今回作成クラウドリソースなし、クラウド費用0円、削除対象・期限なし。既存クラウド環境は未調査。モデル等利用費未取得。実験予算はC開始前に確定。
承認：moruku36配下に公開リポジトリ新規作成、成果物・操作記録の公開、工程コミット・PR作成。マージ・クラウド作成は未承認。

## CI/CD用ディレクトリ
.github/workflows/の空ファイルはworkflow権限不足によりGitHub反映対象外。失敗と代替証跡はevaluation/repository-preparation.md。実際のCI/CD作成時に権限を確認する。
