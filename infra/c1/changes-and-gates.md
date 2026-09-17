# P1：計画差分・承認待ち・証跡対応

正本：PR #17 `38c406c9d260db749f6578375480ff8189b09530`。[CP1](../../experiments/C/C-0/minimal-experiment.md)の業務判断/料金/実験承認欄は変更しない。

|点|今回の実装|影響・残条件|
|---|---|---|
|資源役割|backend bucket/fixture bucket各1、対称key1、plan/apply/cleanup role3、inline policyと付随設定|新規有料サービスなし。bootstrap管理は既存operator。実際のSCP/権限/価格適用は未確認|
|State|bootstrapはlocal、fixtureは初回からS3 native lock|bootstrap Stateの自己移行なし。既存fixture Stateの強制移行機能を作らず停止。単一default workspace、別workspace禁止|
|IAM否定|State本体ではなくbackend内の合成canaryへGet/Deleteを試す|同じ明示Denyポリシーの範囲を確認。本State削除を試した証拠にはしない。canary代替を人間承認|
|lock|条件付きS3 Putで互換lockを保持→Terraform Planの競合→所有ID確認/解除→対照Plan|2つのTerraform applyが競合する試験ではない。native lock protocolの限定確認として承認。timeout/未知応答は未確認|
|データ量|CP1の最大2GBより狭い、各bucket最大60世代/marker・60MiB。45世代/45MiBから新規停止|cleanup余力を確保。ユーザーの2GB容量検証ではない。元の転送1GB/要求上限は増やさない|
|API数量|AWS CLIは1attempt・保守予約。Terraformは人間レビューした各操作予約を事前計上|**内部API数・State保存/応答サイズの厳密計数は未実装**。実環境のPlan前に有限の根拠を示せなければ停止。必要なら追加の計数実装を別指示で補完し、推測の予約値で進めない|
|cleanup|全世代inventory hash承認、exact対象/owner/region/tag/作成receipt、RoleId照合。部分失敗は停止|未知multipartは自動abortしない。復旧情報を守るため端末ファイルの自動再帰削除なし。cleanup失敗・ledger枯渇時は対象を限定した人間の復旧承認|
|権限|bootstrap/最後のrole削除は既存operator、通常roleは自己変更不可|CreateKey等の事前ARN不能権限、必要read/API呼出しとorg追加料金を次の承認で確認。IAM policyのAWS側受理は未実証|

## 費用

CP1税込500円案（計画300＋事故予備200）を未承認のまま継承。別の新規有料資源や無料枠依存は追加していないが、「追加費ゼロを実測した」とはしない。再作成・canary・lock・positive control・State更新によるS3/KMS要求/転送はCP1のTier1 1000、Tier2 2000、KMS10000、送出1GB以内へ予約する。

U-account（組織必須監査/契約等）、U-runner（国内環境/通信/保存）、U-tax-fxは未精算。Terraform内部操作数・実Stateサイズの上限根拠も未確定。既知の約28円/保守212円はCP1数量モデルの参考で、今回の実測請求ではない。全C12,495円＋Uや本番月額10万円を本工程に流用しない。全操作は逐次、15分以内の見込を要求し新規見込300円/数量80%で停止するが、500円をサービス側で強制上限化する仕組みではない。

## 要件→判断→既存試験→予定証跡

|要件/根拠|実装判断|試験IDと将来の証跡|今確認した範囲|
|---|---|---|---|
|REQ-16 / CP1 M10/M13|least privilege、actual account/region/name、canary否定|T12部分：許可対照＋AccessDenied、role/policy摘要、canary version|ガードと分類のmock。実IAMは未実証|
|REQ-18 / M13|local bootstrap/remote fixture分離、承認Plan hash、native lock|T13部分：固定版、Plan hash、lock ID競合、解除後対照、fixture再作成前後|fmt/validate、入力/Plan拒否mock。実lock/再構築は未実証|
|REQ-22 / M06/M11|全世代消去、key依存順、残存receipt|T14部分：全version/marker inventory、NoSuchBucket/NoSuchEntity、PendingDeletion、別日のNotFound|marker含む消去順・誤対象・未知multipart・不存在分類mock|
|REQ-12 / M09|予約上限と未精算Uを分離|T09補助：数量/時間/未反映/残存費の見込、実請求との差|停止ガードだけ。請求/価格適用未確認|
|REQ-08 / M10|東京State＋国内端末、metadata未知経路は個別例外|T06後続：契約/内部経路/所在証跡|所在を証明しない。実験例外は未承認|
|REQ-20|履歴保持、公開機密除外、remote SHA照合|文書検査・PR/Issue/blob一致|今回実施、State/Planを公開しない|

## 次の1工程と開始条件

**人間の回答・承認案への実入力の反映（文書のみ）**を次の1工程として推奨。外部入力は専用account/operator/国内端末、主副・当日枠・後日責任、税/為替/必須課金、metadata/不合格/鍵/段階予算例外、canary/lock代替の受入、Terraformの数量予約の根拠である。未回答に対する推測で承認欄を埋めない。

その後の実環境read/preflight・bootstrap Plan作成には別の操作承認が必要。bootstrap applyはbootstrap Plan承認後、fixture Planはbackend実在binding後、fixture applyはfixture Plan承認後。実装PRのマージやローカル検証成功をこれらの承認にしない。準備成果物が完成しても、live開始条件は未充足である。
