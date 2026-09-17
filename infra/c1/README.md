# C-1準備 P1：実行順と承認境界

2026-09-12追記：[private binding記録](../../evaluation/C-1-private-binding-run.md)はNOT_READY、AWS API 0回。安全な実値入力と暗号化volume確認が残る。[設定手順](private-binding-setup.md)完了後もG1には新しい個別承認が必要。[CP2](../../experiments/C/C-0/approval-2026-09-12.md)と[12段階ゲート](execution-gates-2026-09-12.md)を正本とする。

**今回実施済みなのはコード作成・ローカル検証だけ。以下のAWS操作は将来の手順であり未承認。** 正本はPR #17 / `38c406c9d260db749f6578375480ff8189b09530` の [CP1](../../experiments/C/C-0/minimal-experiment.md)。66/66/66点不合格、LC1未採点、最終選定・C移行保留を保持する。

[計画差分・承認待ち](changes-and-gates.md)／[ローカル検証記録](../../evaluation/C-1-preparation-run.md)。C-1準備成果物の完了とC-1実証完了は別で、後者は未実施。

## 構成とコード

|配置|役割・対象|
|---|---|
|[bootstrap](bootstrap/main.tf) / [権限](bootstrap/iam.tf)|国内暗号化端末のlocal State。versioned private State bucket 1、対称KMS鍵1、plan/apply/cleanup role各1＋inline policy。bucket/鍵にprevent_destroy、force_destroy=false|
|[fixture](fixture/main.tf)|試験用private versioned bucket 1。同じ鍵。Stateは承認後に上記S3へ。再作成対象はこのbucketだけ|
|[c1.py](scripts/c1.py)|入力/承認/対象・時間・費用guard、preflight、作成証跡binding、全世代cleanup、鍵残存、role削除、後日確認|
|[tf_steps.py](scripts/tf_steps.py)|init/Plan/承認済みPlanのapplyを別actionに分離。固定コード・入力・backend・実行バイナリのhash照合|
|[probes.py](scripts/probes.py)|合成canaryによるIAM拒否、条件付きS3 lock holderとTerraform native lock競合/解除後対照|
|[materialize.py](scripts/materialize.py)|非公開入力からtfvars/backend設定を**オフライン**生成。execution_authorized=falseで生成|
|[mock検証](tests/test_guards.py)|クラウド非接続の異常系/ガード/判定検証。IAM自体のシミュレーターではない|

S3のversioning/encryption/public-block/policy/ownershipは2bucketの付随設定で、追加bucketではない。KMS alias、DynamoDB、VPC、DB、計算資源、メール、監視サービス、GitHub Actionsは作らない。

## 0. 次の文書工程で確定する入力（全て未承認）

1. 専用実account、既存operator IAM role、東京、未使用の実験nonce（c1-＋16hex）、実ARN。実IDを公開PRへ入れない。
2. 国内暗号化端末/保存先・外部転送境界、AWS CLI v2の実行版/入手元、Terraformバイナリhash、主副・当日停止/cleanup責任・別日の鍵確認責任。
3. 同日開始/終了JST（最大6h、末尾1h cleanup、5h新規停止）。開始枠を最初の作成より早く設定する場合は保守的に枠開始から計時する。実際の初回課金作成時刻も別記録する。
4. 500円案（計画300＋事故予備200）、税/為替、追加監査/runner/契約費用Uの有限な根拠。15分ごとの未反映/残存込み推計。未知Uはゼロにしない。
5. 不合格下の限定実験、部分C-1、段階予算、管理metadata経路、鍵7日待機、canary/条件付きlock方式の個別承認。
6. Terraformの全API試行/取得byte数の保守的予約枠。provider内部通信はwrapperで厳密に計数できない。コードのmax_retries=1でも元のAPI数を確定したことにはならない。根拠なしにterraform_bound_reviewedをtrueにしない。

メール保存、PITR期間、正常更新損失、本番auth/probe担当・工数は今回対象外として保留する。実験担当者の指定とは別。

## 1. ローカル準備（クラウド非接続）

Terraform **1.13.5**、AWS provider **6.14.1** を固定し各stackの `.terraform.lock.hcl` を同梱。再開環境がWindows amd64以外なら公式checksum/lock対応を再確認する。Pythonは標準ライブラリのみ。AWS CLI v2は将来の実行依存で、今回導入/実API検証はしていない。

本工程で実行したコマンド（可変パスは環境に合わせる）：

```text
terraform fmt -check -recursive infra/c1
terraform -chdir=infra/c1/bootstrap init -backend=false -input=false
terraform -chdir=infra/c1/fixture init -backend=false -input=false
terraform -chdir=infra/c1/bootstrap validate
terraform -chdir=infra/c1/fixture validate
python -m compileall -q infra/c1/scripts infra/c1/tests
python -m unittest discover -s infra/c1/tests -v
```

公式provider取得だけネットワークを使用。StateやAWS認証情報を使うplan/apply/destroyは実行しない。CLI設定には検証用の空設定を指定しcheckpoint/metadata探索を無効化する。

## 2. 人間回答・承認後の実環境preflight/Plan（今回は実行禁止）

公開cloneでlive作業しない。国内暗号化ディスクの**repo外**へbootstrap/fixtureの `.tf` とlockファイルだけコピーし、秘密設定・Plan・State・証跡もrepo外へ置く。入力例のUNANSWEREDはガードで拒否される。標準のCLI入口は次の形で、live flagだけでは実行できない。

```text
python infra/c1/scripts/c1.py check-config --config <private-config.json>
python infra/c1/scripts/materialize.py --config <private-config.json> --out <private-directory>
python infra/c1/scripts/c1.py <action> --config <private-config.json> --approval <private-approval.json> --live
```

configは [入力例](config.example.json)、承認記録は [未承認例](approval.example.json)を非公開でコピーして用いる。生成tfvarsは初期false。人間の実行承認を受けた版だけtrueとし、各tfvars/コード/binary/configのhashを承認記録に固定する。承認JSONは署名基盤ではなく、AIや利用者がtrueを書いたこと自体を人間承認の証拠にしない。別途承認者・日付・版・許可actionの記録が必要。

|順序/action|承認対象・前提|確認結果・次の停止点|
|---|---|---|
|preflight|環境/操作read範囲の承認後。各profileの実主体をSTSで照合|bucket2名/role3名が不存在であること。AccessDeniedを不存在にしない。既存同名は採用/importせず停止。preflight receipt hashを保存|
|bootstrap-init|空の非公開workdir、local backendのみ。固定lock依存使用|local State配置が確定。既存Stateがあれば復旧判断へ停止|
|bootstrap-plan|承認済みoperator、同account入力、local State|State bucket1/key1/role3＋付随設定だけのPlanと費用/操作を人間へ。ここで**停止**|
|bootstrap-apply|人間がbootstrap Planの全差分・hash・価格・権限を承認|最初の課金開始。local State/backupを保全し、output bindingの実key ARN/rolesを非公開configへ反映、config承認版を更新|
|bind（bootstrap後）|作成Plan hash/State lineageとpreflightの人間照合|既存由来を取り込まず実作成bucket/key/RoleIdをreceipt化。fixture未作成ならbackendだけ記録可。部分作成失敗時は下の回復分岐|
|fixture-init|実backend/key入力を再生成しbackend_config hash承認。fixture State未作成|空のfixture Stateの保存先をS3に初期設定。実backendへ接続するので操作承認が必要。**bootstrap Stateは移さない**|
|fixture-plan|backend作成後の実keyを使う別Plan。allowlist検査＋全内容人間確認|fixture bucket1＋付随設定のみ。bootstrap Planの承認は流用せず**停止**|
|fixture-apply|fixture Plan hashと対象/費用/期限を別承認|fixture作成。再度bindして作成receiptを更新。ここまででIAM/lock/削除を実証したことにはならない|

bootstrapをremoteへ自己移行すると最後の削除依存が循環するためlocalに保持する。fixtureは初回からS3 backendを使い、移す既存Stateがない。この手順の「State移行」は保存先の初期bindingである。既存のlocal fixture Stateや既存backend設定を検出した場合、コードはforce-copyをせず停止する。lineage/serial/全copyを照合した別の移行承認なしに手動移行しない。

既存operatorに必要なのは、この実験名へのS3/IAM設定/作成/削除、同key管理、role assume、STS identity。KMS CreateKeyなど作成前ARNが指定不能のActionはResource=*にせざるを得ないが、東京/Experiment request-tag/短命sessionで範囲を縛った実policyをPlan前に人間確認する。IAMはglobalなのでregion条件だけで代替しない。通常apply/plan roleへIAM自己変更や鍵削除権限を追加しない。SCP/permission boundary等で不足が出たら権限を自動拡張しない。

## 3. 承認後の限定確認とfixture再作成

- **iam-probe / T12部分**：operatorがbackendの `denied/canary` を合成内容でseedしVersionIdを確保。apply roleはfixtureのsynthetic/canaryをPut/Getして対照成功を確認。backend canary Get/DeleteがAccessDeniedなら期待拒否。想定外成功は失敗、NoSuchKey/期限切れ/通信失敗は未確認として停止。実StateのDeleteは発行しない。
- **lock-probe / T13部分**：全writer停止後、apply roleが本来のtflockキーをIf-None-Match=*で取得しTerraform互換lock情報を保存。Terraform planが当該IDの412/PreconditionFailed＋lock取得失敗を返すことを確認。自分のIDを再読取して一致した場合のみlockを解放し、同じPlanが成功する対照を取る。初回成功は失敗、認証エラー等は未確認。タイムアウト/所有者不明はlockを残して人間確認し、force-unlockしない。
- **再構築 / T13部分**：全writer停止、fixtureの全世代inventoryを取得・hash承認してcleanup-fixture。backendを保持し、fixture-planが同じ名前・コードの6設定resourceのcreateだけになることを確認。**再作成Planを再承認**してfixture-apply、bind更新。新key/role/backendは作らない。再構築の結果はPlan hash、bucket識別・設定、前後receiptで記録する。
- いずれも無負荷・無故障注入・無メール。失敗/未確認は停止し、勝手に修正apply/反復しない。

## 4. cleanupと残存証跡 / T14部分

5h又は承認終了−1hで新規作業停止。全writer/session利用者の停止を確認し、15分以内の費用見込を記録する。期限を過ぎても既承認対象のcleanup資格は使えるが、期限超過の成功扱いや保持延長承認にはしない。

1. **private export**：bootstrap/fixture State、必要な復旧copy・直近Plan・非機密識別台帳を国内暗号化ディスクへ保全。破棄は依存不存在後。State pull等の読取も承認済み操作一覧とAPI予約枠内で行い、生Stateを標準出力やGitHubへ送らない。
2. **cleanup-fixture**：receiptの作成由来、bucket名、owner account、東京、Experiment tagを照合。全version/delete marker一覧をprivate保存し、hashを人間確認してpurge_inventory_sha256へ固定。multipartがあれば自動abortせず停止。各versionを指定して消去→再一覧空→bucket削除→NoSuchBucketを確認。
3. **cleanup-backend**：fixture不存在・全writer停止・State export確認後のみ、State本体/lock/canaryの全世代とmarkerを上と同じ順序で削除。中断後にremote Stateを戻して再applyしない。
4. **schedule-key**：対象bucket2名の不存在とローカル暗号化依存の解消を確認。key ARN/型/単一region/tagを照合し7日で予約。キーPendingDeletion、KeyId、DeletionDate、region、後日責任参照、時刻を**private receipt**へ保存。既にPendingDeletionなら予定日を再取得し再予約しない。receipt未保存ならrole削除へ進まない。
5. **cleanup-roles**：既存operatorが作成receiptのRoleId/ARN/tagを確認。inline cp1-scope以外やattached policyがあれば停止。限定inline policy→roleを消しNoSuchEntityで確認。cleanup自身の権限ではなく既存operatorで最後を行う。
6. **国内copy整理**：鍵以外の依存不存在と必要証跡の保存確認後、local State/backup/Plan/lock実体/一時canaryを削除する。これは手動承認付き端末操作とし、コードは端末内を再帰削除しない。障害時には復旧情報を先に捨てず、保持理由/期限/担当/追加費の例外判断へ。
7. **別日のresidual**：別工程のread承認が必要。実DeletionDate以降＋24h以内を担当が確認。NotFoundExceptionのみ不存在、AccessDenied/通信失敗は未確認。PendingDeletionは引き続き残存。期限後の確認結果を保存するまで鍵台帳を閉じない。実行予約は今回作らない。

再試行時は部分消去後のinventoryを取り直して再承認する。bucket名/tagだけで削除しない。途中で名前が同じでも由来/State/RoleIdが不一致なら停止。bootstrap apply失敗でrole群未完成、receipt未作成、API応答消失、ledger枯渇等の場合は自動cleanupの前提が揃わない。既存operatorがそのPlan/ローカルState/作成時刻から対象を限定してread棚卸し→個別cleanup案を人間承認する。新規実験・無関係資源削除・権限拡張で回避しない。失敗を「残存なし」にしない。

## ガードの限界・運用量

この実装は今回の小確認用に **各bucket最大60version/marker、各bucket合計60MiB、payload1MiB** に狭めた。multipartは拒否し、ライフサイクル/複製/追加通信を作らない。CP1の最大2GBを使い切る実験ではない。

AWS CLI wrapperは1attempt設定、各呼出しを保守的にTier1 1＋Tier2 1＋KMS 2＋応答1MiBとして事前予約する。実際のmeterとは一致しない。新規作業は各上限80%まで、残20%はcleanup用。大量一覧/大応答/再試行が出たら停止する。request.guardはledger更新の同時実行防止だけであり、複数のliveプロセスを許可する機能ではない。全actionを逐次実行する。

Terraformについては各init/plan/apply前に承認済みの予約数量をledgerへ加算し、内部呼出しの実測カウンターを備えたとは主張しない。予約の根拠が未確定ならlive不可。新規作業の残時間が3分未満ならTerraformを起動しない。最長180秒、lock確認各60秒でtimeout時は部分状態不明として停止。予算通知/時間ガード/上限予約はクラウド請求の強制上限や自動削除保証ではない。

## 管理metadataの限定例外

根拠は固定PR #17が継承する [LC1経路台帳](../../experiments/B/B-2/limited-completion/iam-operations-data.md) のCloudTrail等control-planeとState/CI行。

|対象データ・経路|未確認点と限定実験への影響|
|---|---|
|account ID、IAM role ARN/name、STS session/操作時刻、接続元IP、service request ID|国内端末→東京STS/各API、IAMのglobal control-plane、AWS内部処理/監査・サポート等への経路。全metadataの保存/転送国・契約範囲は未確認|
|State/Plan、合成object、KMS encryption context|Stateの物理配置は東京S3/private、端末copyは承認国内保存先の設計。region設定はサービス内部metadataも全て国内という証拠ではない|
|コード/非機密要約→公開GitHub、公式配布取得|GitHub/配布CDNに実account/State/Plan/資格を載せない。GitHub hosted runnerによる権限付きPlan/OIDC連携は本実装対象外|

例外対象はこの限定実験に不可避なaccount/操作metadataの未確認経路のみ。業務data/受信メール/本番PII/本番全copy国内保存を包括免除しない。追加の実account必須監査が国外転送又は有料化するなら例外・費用を再判断する。未知経路を「合成だから無害」と扱わない。
