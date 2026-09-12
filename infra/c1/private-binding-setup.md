# C-1 preflight private binding 手順

固定実装：PR #18以降の `infra/c1`。この手順はAWSへ接続せず、実値をrepo外へ設定して `check-config` まで行う。preflight、`--live`、Terraformは実行しない。

## 固定入力と命名

private JSONの主なキーは `account_id`、`region`、`experiment_id`、`operator_arn`、`backend_bucket`、`fixture_bucket`、`state_key`、`roles.plan/apply/cleanup`、`profiles.operator`、`evidence_dir`、`domestic_encrypted_workspace_confirmed`。完全な構造は `config.example.json` を参照する。次回preflightには別のprivate承認JSONと絶対時刻が必要で、今回作成しない。

- `account_id`：12桁。固定コードのdummy拒否集合と同一数字12桁は禁止。
- `region`：`ap-northeast-1` 固定。
- `experiment_id`：`c1-[0-9a-f]{16}`。既存方針上private管理とし、公開run IDには使わない。
- `base = experiment_id + "-" + account_id`
- bucket：`base + "-state"` と `base + "-fixture"`
- State key：`state/` + `experiment_id` + `/terraform.tfstate`
- role ARN：同一accountの `role/` + `base` + `-plan|-apply|-cleanup`
- `operator_arn`：同一accountの既存role ARN。実値はAWSから取得せず本人の管理情報を入力する。

手動上書き、別region、別数量は固定guardで停止し、CP2の承認も失効する。

## Windowsでの安全な入力

1. BitLocker等の保護状態をWindows UI又は管理者権限のローカル確認で確認する。同期サービスの対象外にあるローカルディレクトリを選ぶ。OneDrive、Dropbox、Google Drive配下は使わない。
2. 次のコマンドはプレースホルダーを実値へ置換して実行せず、`Read-Host`のプロンプトへ入力する。入力値はコマンド履歴へ残らない。

```powershell
$privateRoot = Read-Host '<PRIVATE_EVIDENCE_PATH>'
$awsProfile = Read-Host '<AWS_PROFILE>'
$expectedAccount = Read-Host '<EXPECTED_ACCOUNT_ID>'
$operatorArn = Read-Host '<EXPECTED_OPERATOR_ROLE_ARN>'
```

3. `$privateRoot` がrepo・同期rootの外側で、暗号化されたローカルvolume上にあることを目視確認してから、そのディレクトリだけを作る。ACLは現在ユーザーとSYSTEMだけへ限定し、親や広いディレクトリを変更しない。

```powershell
New-Item -ItemType Directory -LiteralPath $privateRoot
icacls $privateRoot /inheritance:r /grant:r "$($env:USERNAME):(OI)(CI)F" "SYSTEM:(OI)(CI)F"
```

4. 実験IDは暗号学的乱数16進16桁を付けてローカル生成し、表示しない。上記式で5名称を算出してprivate JSONへ書く。`config.example.json`を構造の手本にしても、実値入りファイルはrepoへ置かない。
5. 指定profileの存在は、そのprofile名だけを使って共有config/credentialsの該当sectionがあるかをローカル判定する。profile一覧・section内容・credentialを表示しない。期限と接続可否は「実接続未確認」とする。
6. 本人管理PC、日本国内、保存先暗号化、同期外、確認JST/UTCをprivate宣言へ保存する。公開版は成否と時刻だけにする。

## オフラインguard

次だけが固定実装のオフライン入口である。標準出力のconfig/code hashもprivate証跡へ保存し、公開しない。

```powershell
python infra/c1/scripts/c1.py check-config --config <PRIVATE_CONFIG_JSON> *> <PRIVATE_GUARD_OUTPUT>
```

`check-config` は `validate_config` の後に終了し、`Aws`、AWS CLI、Terraformを呼ばない。`preflight`等のactionは `--live` と承認JSONを通過すると `run_action` からAWS CLIを呼ぶため、今回実行禁止。固定guardが直接確認するのはaccount/region/experiment/命名/同一account operator ARN/repo外保存先である。profile存在、volume暗号化、同期外、ACL、国内PCは上記のローカル手動gateを併用する。

すべて成功しても次回最大6 APIの承認にはならない。private設定、固定hash、ローカル確認時刻を人間が確認し、改めてG1を承認する。
