# G2：管理画像IAM・保守責任・国内データ経路

改版LC1、設計のみ。根拠：C-0 [第2群](../../../C/C-0/decision.md)、M04/M07/M10（メール境界はM01）、B-3 F04/F05/F11、REQ-02/03/08/13/14/16/18。[B-2 design](../design.md)の通常app Get権限を維持し、管理画像更新/保守と保存経路の不足を具体化する。

## 管理画像の専用取込経路（条件付き設計案）

管理者個別ID＋MFA→期限付きupload role→東京S3 `quarantine/<batch nonce>/`→専用取込Fargate task→検査済み `published/<content ID>/<digest>`→DBの画像参照切替→通常app Get→ALB→利用者。利用者アップロード・任意URL fetch・public/署名付き画像URLを追加しない。quarantineはCRR対象外、publishedのみ国内DR対象。管理者のローカル原本はこの経路の管理対象外として保存境界の回答時に確認する。

常設の管理API/追加Webサーバーを作らず、権限を持つ管理者が承認batchを登録し、固定task definitionの取込jobを起動する。DB登録は管理用接続から限定手続へ行い、バケットへ置いたことだけで公開許可にしない。通常のコンテンツ編集画面は検査済みdigestだけ参照できる。実際のCLI/UI実装は別工程。

|主体|許可範囲・拒否事項|認可/監査|
|---|---|---|
|upload role|承認batchのquarantine prefixへのPutと必要multipartのみ。published/台帳/backupのwrite/read/delete不可。対象鍵の必要暗号化操作だけ|MFA一時昇格、upload期限とbatch制限。role付与者と承認者を記録（担当未回答）|
|import launcher|国内実行環境の承認済み起動処理だけが保持するrole。固定cluster/task definitionのRunTask、固定import/execution roleへのPassRoleのみ。人間upload roleにはRunTask/PassRoleを与えない|起動処理が許可リストから引数を生成し任意image/command/role/network overrideを受け付けない（IAMだけで全override制約を実現したとはしない）。同accountとPassedToService制限。[IAM根拠](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html)|
|import task role|IAMはquarantine/publishedの専用prefixまで限定し、batch/contentの制約はDB承認記録と取込処理でも強制。専用secret読取り、DBは画像manifest登録/比較切替の限定手続だけ、会員/認証表は権限なし|一般taskからAssumeRole不可。DB接続はprivate、専用SG、TLS verify-full。不正batch/digestとcontent version競合を拒否|
|app task role|publishedの許可prefix Getのみ、quarantine Get/Put/PassRoleなし|他人/未検査digestはDB認可で拒否。roleを拡大しない|
|cleanup role|期限切れquarantine/published旧世代の個別削除・multipart abortのみ。IAM付与・DB切替不可|G1の原期限、専用実験資材manifestに限定。新しい公開画像を期限だけで削除しない|

必要Actionの候補はS3 GetObject/PutObject、一覧系、AbortMultipartUpload、DeleteObjectVersion等を職務別に分割。bucket policy・KMS key policy・task trustも同じ境界にする。resourceを限定できない一覧APIはaccount/regionを実行側で照合し、書込み/削除は取得した一覧をそのまま使わず承認manifestと突合する。権限付きtask definition作成/PassRole付与は実装前のPlanレビュー対象。

検査順序は①batch承認/期限/固定object version②サイズ5MiB/枚上限③JPEG/PNG/WebPの実体/MIME照合④decode後pixel数20MP・frame1・処理時間10秒・task memory境界⑤metadata除去/再encode⑥検査済みhash/version記録⑦DB content version比較による原子的参照切替。5MiBは既存仮定、追加の20MP/10秒は保護の初期設計値で性能保証でない。超過/偽装/破損はrejectし、SVG/実行形式/任意URLは扱わない。

取込失敗は公開参照を旧正常版に維持し、未公開objectを24h以内の内部目標で削除。upload元のすり替えはversion/hash不一致で拒否。DB切替競合はやり直し、人間承認なしにcontentを上書きしない。成功後の元rawは24h以内、公開画像は業務保持、旧版はG1の期限を継承。jobが途中で止まってもbatch状態（承認/検査/公開/失敗）から冪等再開する。鍵失効をraw画像の削除確認の代わりにしない。

監査には時刻・操作種別・batch nonce・対象content/version・判定/理由コード・実行role・承認参照を記録し、画像本体/EXIF/本文/認証情報を記録しない。actorの対応表は国内アクセス制限store、公開証跡は合成IDだけ。監査書込みが失敗したら公開切替を止める。偽装失敗の追跡とPII非記録を両立するためraw request保存に逃げない。

## データ/metadata経路台帳

|データ|保存・転送案と権限|保持/消去・未解決|
|---|---|---|
|会員/auth/変更履歴|利用者TLS→ALB→private app/DB writer東京。DB app roleのowner scope。backup/dumpのみ大阪へ|G1の台帳/原期限。IP等の制御metadataは下段と別確認|
|管理画像|管理端末→東京quarantine→import→published→app配信。大阪は検査済みcopyのみ|raw24h/旧版G1。画像入力のpixel/memory上限検証待ち|
|outbox/メール|DB東京→worker→SES東京→受信者。sink案ではSES送信権限なし、国内DBへ状態だけ記録|受信側の適用範囲/SES内部metadataは未回答/未確認。送信0通の試験を配送要件合格にしない|
|app/probe/削除監査|東京/大阪のCloudWatch、PIIを除いた許可フィールドのみ。collector/監査writerはwrite、通常appは削除不可|30日案。管理者対応表/個人情報混入はG1期限を適用。追加audit event/取込量はU|
|CloudTrail等control-plane|必要管理eventを国内保存先へ集約する設計、IAM/STS/SES/SNS等のサービス内部処理/転送保証は契約範囲確認が別途必要|保存先regionだけで全metadata国内と判定しない。避けられない未確認経路はC-0 E12で明示例外又は使用停止|
|DNS/WAF/ALB観測|Route53 public query logは国外保存の既存指摘により有効化しない。国内probe/app観測、WAF redaction＋sample/body capture抑制。ALB raw logを保存しない案を継承|DNS query監査欠落・global処理を隠さない。国内監査網羅性は未成立。ログ無効化だけでREQ-08/16適合にしない|
|State/Plan/CI|東京の非公開暗号化State、必要な復旧copyのみ大阪。公開GitHubはコード/マスク要約、クラウド権限付きPlanは国内実行環境内|G4で期限と権限。GitHub hosted runnerへState/Plan/実metadataを送らない。OIDC/IAM連携metadataの経路は別確認|

設定で制御できる国内保存先/PII抑制と、契約回答が必要なサービス内部経路を分離した。これ以上の所在地保証を推測で付けず、限定実験の対象データ・経路だけを明示して承認判断へ渡す。

## 認証・監視保守の役割と作業（実在担当・工数確保は未承認）

|役割案|具体責務・権限・引継ぎ|必要入力/影響|
|---|---|---|
|auth主/副|週次脆弱性確認、月次更新候補、MFA/session失効・DB CA変更の互換確認。code reviewとdeploy承認を分離、副担当も旧digestへrollback可能|氏名を捏造しない。採用framework/拡張のversion・support/ライセンスを実装準備で固定。担当割当なしは運用承認不可|
|probe主/副|欠測/unknown確認、通知不能時の連絡、SLI定義/監査量変更レビュー。自己監視失敗をgoodにしない|主副の役割、連絡経路、月間工数は要回答。auth主との兼任も自動確定しない|
|基盤主/副・停止責任者|IAM付与/期限/backup/鍵/費用確認、承認manifest外を停止。休暇時の権限引継ぎを事前確認|既存専任1名へ全役割を押し込まない。夜間即応保証なしを維持|

初期auth5〜10人日/probe3〜5人日、保守auth+probe8〜16h/月＋基盤16〜24h/月は既存未承認仮定。推奨は開発側auth/probe主副＋基盤主副の分担案、受け入れ不能ならmanaged代替の費用/所在地調査を別判断（今回選定しない）。脆弱性対応は既知正常versionへの限定rollback/危険機能停止を判断し、無承認で夜間全面更新しない。休暇/担当不在演習はT10であり、架空の演習時間を入れない。

## 容量・費用・予定証跡と状態

import jobは通常appの容量と分離し1vCPU/2GiBの既存task形状を初期候補とする。稼働h、public IPv4 h、raw/旧版GB、検査log/監査、KMS/API、DB manifest増は[G4費用](../cost.md)へ。常設費を0と断定せず、要求が連続ならjob時間とqueue滞留を再見積。5MiBでもdecode安全性は実証待ち。

T01/T02/T12（C-2）：通常appのwrite拒否、未承認batch/期限切れ/すり替え/偽装/過大画像拒否、content旧版維持、監査欠落時公開停止。T06（C-1のState/監査、C-2/9）：保存/転送台帳と公式/契約回答、設定export。T10（C-4/10）：担当主副承認と実演習。予定証跡はredacted policy、合成batch要求順、object/DB version、拒否/cleanup結果、ログPII検査、担当受入記録。

専用経路・職務権限・検査/監査/保守タスクのDは補完。実IAM/入力検査/PII抑制はE、受信側範囲と担当工数はH、内部metadataの所在地保証は資料/契約確認待ち。未確認を技術試験だけへ移管しない。
