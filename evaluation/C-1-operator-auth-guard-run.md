# C-1 Operator認証ガード修正・ローカル検証記録

日付：2026-09-13。起点はPR #21 head `7e9b133c750db93953e0e5e260c9c4c0a65a5a8d`、比較先 `codex/c1-private-binding` / `7e9b133c750db93953e0e5e260c9c4c0a65a5a8d`。直接依存#21、間接#20→#19→#18→#17→#16→#15（全て未マージ）。

## 修正と判定

STS前の完全operator ARN入力を廃止し、privateのaccount、`assumed-role`、完全role名、認証方式、profileへ置換した。SSOはPermission Set名と実予約Role名を分離し、AssumeRoleはlocal role ARNを構造parseする。STS応答はpartition/service/account/principal/role/sessionを順に構造照合し、部分一致・root・IAM user・federated-user・percent encoding・不正segmentを拒否する。公開結果には実識別子を含めない。

ローカルAWS metadataを値非表示・非通信で分類した結果はprofile 2、SSO 0、AssumeRole 0、credential_process 0、静的2、判定不能0。静的profileは不許可で、許可可能な既存profileは確認できなかった。Role実在はAWS未接続のためUNDETERMINEDであり、新設の要否も未確定。

## 検証結果

|確認|結果|
|---|---|
|Python syntax|PASS|
|既存mock 27件の回帰＋認証追加9件|36/36 PASS|
|成功系|AssumeRole、SSO由来、IAM role path正規化、offline config/profileを確認|
|拒否系|account/partition不一致、root/user/federated、部分一致、encoding、欠落、malformed、別service、静的key、必須入力、公開log漏えいを確認|
|Terraform fmt/validate|未実施。`.tf`とprovider lockに起点差分がなく、本変更はPython/JSON/文書だけのため再実行不要と判断|
|AWS通信/API|0回。STS/S3/IAM/KMS/請求0、retry 0|
|変更操作|Role/profile/credential/Plan/State/資源の作成・変更・削除なし|

コード修正とRole設計文書は承認済み。本PRの新固定版、AWS API再実施、Role作成、profile変更、SSO login、Plan/apply/probe/cleanupは未承認。次工程は既存認証経路の選択又はOperator Role新設方針を人間が決め、別承認のもとで認証設定を用意する工程である。private binding再実施とpreflightには進んでいない。

実モデル識別、トークン、料金、実作業時間は取得できず不明。資源・請求の最新状態も未確認である。

