# 再開情報

更新2026-09-09。A-1完了1745dfe、A-2設計文書作成。全要件適合やA-3合格を意味しない。
PUBLIC保存先：https://github.com/moruku36/cloud-validation-level3-astra-light 。公開範囲・所有者は指定済み。
ブランチa2/aws-design、base origin/a1/requirements=1745dfefe71e11a9df077eb247982f0f5f7616d7。PR #3未マージ、mainは要件を含む前提にしない。A-2のPRはa1/requirementsを比較先とする。初回設計81cab82、後続に算術表現訂正・追跡情報更新。最新commitはgit rev-parse HEADで確認。

## 確定・仮定・未解決
ECS/Fargate ARM常時2AZ＋RDS PostgreSQL同期Multi-AZを条件付き採用。ALB/WAF東京、CloudFront不採用（国内保存を優先）。task public IP＋SGで入口制限、DB/S3はprivate。Cognito/SES東京。詳細はdesign.md。
小計82,682円、20%余裕込み99,218円、為替150円・税10%仮定。価格主要単価取得済み、小費目/通信予算枠・性能増強は未確定、予算余裕782円のみ。
片AZ1task100RPS、DB credit、全依存の30分上限、メール転送先/受信者保存、PITR4h/地域復旧、測定実装は未検証。Issue #4 OPEN、各論点に判断/根拠/検証方法を保存。回答済み業務条件は再質問しない。
BはAWS指定を継承せず3社比較。C-0まで実験上限・権限・期限未承認。指定モデルGPT-6 Astra Light、実行モデル識別未確認。実残りトークン数未取得。

## 次回1工程
**A-3のみ**。明示実行指示待ち。今回はA-3正式採点・包括レビュー未実施。
読む順：本ファイル、resource-inventory.md、experiments/A/A-2/design.md・cost.md・issue4.md、必要に応じて24要件/正式配点/出典。初回設計を保持し、根拠・予算/性能/DRをレビュー、要件→設計→検証対応を評価し、自己採点、人間欄空欄、修正前後を保存。Bへ進まない。
必要コマンド：git status --short、git rev-parse HEAD、git ls-remote origin a2/aws-design（remote一致）、gh pr view（A-2番号）--json baseRefName,headRefOid,state（base a1/requirements・OPEN）、gh issue view 4 --json body,state。
公式価格の完了調査は再実行せず、通信/小費目と代替案費用の未確定部分だけ必要性を判断する。ADR要件IDと未検証を追跡。詳細IaC実装はまだ不要。

## 資源・費用・承認
今回作成資源なし、クラウド利用費0円、削除対象/期限なし。既存アカウント全体未調査。モデル等費用未取得。上記設計額は実費ではない。
承認された今回範囲A-2設計・公開GitHub保存/PR/Issue更新。マージ・クラウド作成は禁止。次回A-3は別指示。workflow権限不足はC前対応、今回拡張なし。
