# クラウドアーキテクチャ検証 LEVEL3 (AWS構成編)

本リポジトリは、**曖昧なビジネス要件・制約からAI（自律型エージェント）が実践的かつ合理的なクラウド構成を設計・判断・評価できるかを検証するプロジェクト**（LEVEL3検証）の記録および成果物です。

クラウドエンジニアや開発チームが設計意図・検証結果・課題を直感的に把握できるよう整理しています。

---

## 1. プロジェクト概要

- **目的**: 曖昧なビジネス要件に対し、AIが適切な要件定義、アーキテクチャ選定、コスト見積、耐障害・運用設計を行えるかの検証
- **検証対象モデル**: GPT-6 Astra Light
- **検証シナリオ**:
  - **Phase A (本フェーズ)**: AWS単一クラウドにおける最適構成の設計と自己評価
  - **Phase B (次フェーズ・保留中)**: AWS / Azure / Google Cloud の3大クラウド比較選定
  - **Phase C (将来フェーズ)**: IaC実装・実機デプロイ・カオスエンジニアリング（障害試験）

### 現在のステータス
- **進捗**: Phase A（A-1 要件整理 〜 A-3 設計評価）完了
- **設計自己評価スコア**: **65点 / 100点**（合格基準80点に未達、**採用承認保留**）
- **保留の主因**: 外形監視（CloudWatch Synthetics Canary）費用の精緻化に伴う**月額予算（税込10万円）の超過**（修正後: 約11.01万円〜予備費込約13.22万円）
- **クラウド実リソース**: 未作成（Phase Aはペーパー設計・評価のみ、クラウド利用費0円）

```mermaid
flowchart TB
  subgraph PhaseA ["Phase A: AWS単一設計（完了・評価保留）"]
    direction LR
    A1["<b>A-1 要件整理</b><br/>曖昧要件から24要件定義"] --> A2["<b>A-2 AWS設計</b><br/>ECS+RDS Multi-AZ設計"] --> A3["<b>A-3 設計自己評価</b><br/>61→65点 (予算超過で保留)"]
  end
  subgraph PhaseB ["Phase B: 3社マルチクラウド比較（保留中）"]
    direction LR
    B1["<b>B-1 共通比較基準</b>"] --> B2["<b>B-2 詳細設計</b>"] --> B3["<b>B-3 3社評価選定</b>"]
  end
  subgraph PhaseC ["Phase C: 検証・障害試験（将来）"]
    C1["<b>C 実装・カオス試験</b>"]
  end

  PhaseA -->|人間の承認・指示後| PhaseB
  PhaseB --> PhaseC

  classDef done fill:#d4edda,stroke:#28a745,stroke-width:2px;
  classDef pending fill:#fff3cd,stroke:#ffc107,stroke-width:2px;
  classDef future fill:#f8f9fa,stroke:#6c757d,stroke-width:1px,stroke-dasharray: 3 3;
  class A1,A2 done;
  class A3 pending;
  class B1,B2,B3,C1 future;
```

---

## 2. 業務・システム要件サマリ

| 項目 | 要件仕様 | 設計上のポイント・制約 |
|---|---|---|
| **サービス形態** | 新規国内B2C Webサービス | 会員登録、ログイン、一覧・詳細、お気に入り、管理機能 |
| **ユーザー規模** | 初期1万人 → 3年で100万人 | 月間100万PV、通常10 RPS、ピーク100 RPS（15分/日）、同時接続500人 |
| **目標SLA / 可用性** | 暦月 99.9% 以上 | 東京リージョン内 2つのAZ（Availability Zone）によるマルチAZ冗長化 |
| **目標RTO / RPO** | **RTO ≦ 30分 / RPO ≦ 5分** | 単一AZ障害時は自動フェイルオーバー、復旧後300秒（5分）の連続安定監視 |
| **データ主権・保存** | **日本国内限定保存** | 東京リージョン保管、大阪リージョンへ日次DRバックアップ（PITR 35日） |
| **月額予算上限** | **税込 100,000 円 / 月** | 本番＋最小開発検証環境、通信・監視・セキュリティ・バックアップ全込み |
| **運用体制** | 開発5名・インフラ専任1名 | 平日日中運用、夜間即応なし（**夜間はマネージドサービスによる自動復旧必須**） |

---

## 3. アーキテクチャ概要 (AWS)

専任1名の運用負荷を抑えつつ、同期整合性（SQL）と夜間の自動復旧を両立するため、**AWS Fargate (ARM) + Amazon RDS PostgreSQL (Multi-AZ)** を採用構成案として選定しました。

### システム構成図

<p align="center">
  <img src="experiments/A/A-2/architecture.jpg" alt="実験構成図: moruku36/cloud-validation-level3-astra-light (AWS構成)" width="100%" style="max-width: 900px; border: 1px solid #ddd; border-radius: 6px;" />
</p>

### 主要コンポーネントと選定理由
- **DNS / ネットワーク**: Route 53 (DNSルーティング) + ALB (HTTPS終端・2AZ負荷分散)
- **セキュリティ**: AWS WAF (ALB直前でRate Limitおよびマネージドルール適用)
- **アプリケーション実行基盤**: AWS Fargate (Graviton ARM, 1vCPU / 2GB) × 2AZ常時稼働（最小2〜最大6タスク）
  - *選定理由*: EC2に比べOSパッチ・AMI運用保守工数を削減。Kubernetes (EKS) は専任1名体制での運用複雑性を考慮し不採用。
- **データストア**: Amazon RDS for PostgreSQL (`db.t4g.medium`, gp3 50GB, 同期Multi-AZ)
  - *選定理由*: 会員情報・トランザクションの強い整合性担保、スタンバイ系への自動フェイルオーバー（60〜120秒目安）。
- **認証基盤**: Amazon Cognito (東京リージョン・Lite構成)
- **オブジェクト・バックアップ**: Amazon S3 (プライベートバケット・VPCエンドポイント接続)
- **ディザスタリカバリ (DR)**: 大阪リージョンへの日次DBスナップショット転送・S3クロスリージョン複製（Cold DR構成）

---

## 4. 費用評価・ボトルネック（A-3評価結果）

初期設計（A-2）では月額約8.27万円（予備費込約9.92万円）と予算枠内に収まっていましたが、A-3の設計レビューにて**外形監視（Canary）費用の計上漏れ**が発覚し、予算超過となりました。

### 月額費用と予算上限の比較

| 評価フェーズ | 月額費用 (税抜USD) | 月額費用 (税込・150円換算) | 予算 (10万円) に対する判定 |
|---|---:|---:|---|
| **A-2 初回設計 (予備費なし)** | 501.10 USD | **82,682 円** | 適合（約1.73万円の余裕） |
| **A-2 初回設計 (予備費20%)** | 601.32 USD | **99,218 円** | 適合（782円の余裕） |
| **予算上限ライン** | - | **100,000 円** | **基準線** |
| **A-3 修正版 (予備費なし)** | 667.54 USD | **110,144 円** | **10,144 円 超過 (110.1%)** |
| **A-3 修正版 (予備費20%)** | 801.05 USD | **132,173 円** | **32,173 円 超過 (132.2%)** |

### コスト超過の要因と主な内訳
- **監視費用の見直し**: 東京・大阪両拠点からの毎分Canary外形監視（CloudWatch Synthetics）費用（+166.44 USD / 約2.7万円）が必須となったため。
- **改善代替案（未承認）**:
  1. Canaryを専用サービスから軽量Lambda定期実行へ内製化（運用保守工数とのトレードオフ）
  2. 大阪Canaryの実行頻度を毎分から5分へ緩和
  3. 月額予算上限を約13.2万円へ調整・引き上げ

---

## 5. ドキュメントマップ

本検証に関する詳細資料は、目的別に以下のディレクトリに整理されています。

### 企画・要件・ルール (`docs/`)
- [要件定義・全体方針](docs/requirements.md) : ビジネス背景、制約条件、前提事項の整理
- [実行ポリシー](docs/execution-policy.md) : AIエージェントの作業手順・禁止事項・評価方針
- [正式業務回答](docs/sources/business-answers-2026-09-08.md) : ヒアリングに対する顧客側の正式回答

### Phase A: AWS単一クラウド検証 (`experiments/A/`)
- [**★ LEVEL3-A 総合検証結果レポート**](experiments/A/final-report.md) : **A-1〜A-3の全結果・採点・課題を集約したメインレポート**
- **A-1: 要件定義フェーズ**
  - [24要件一覧・受入条件](experiments/A/A-1/requirements.md) / [質疑応答台帳](experiments/A/A-1/questions.md) / [リスク・仮定一覧](experiments/A/A-1/assumptions-risks.md)
- **A-2: アーキテクチャ設計フェーズ**
  - [基本設計・3案比較](experiments/A/A-2/design.md) / [構成図](experiments/A/A-2/diagram.md) / [復旧・運用・IaC方針](experiments/A/A-2/recovery-operations.md) / [初期費用概算](experiments/A/A-2/cost.md) / [ADR意思決定記録](docs/decisions/ADR-A2-001.md)
- **A-3: 設計評価・レビューフェーズ**
  - [自己評価スコア表 (61→65点)](experiments/A/A-3/scores.md) / [指摘事項・改善仕様](experiments/A/A-3/revised-design.md) / [予算再監査レポート](experiments/A/A-3/budget.md) / [24要件追跡マトリクス](experiments/A/A-3/traceability.md)

### 評価・検証プロセスログ (`evaluation/`)
- [A-1 操作検証記録](evaluation/A-1-run.md) / [A-2 操作検証記録](evaluation/A-2-run.md) / [A-3 操作検証記録](evaluation/A-3-run.md)
- [人間の介入記録台帳](evaluation/human-intervention.md) : AIの自律性と人間による介入回数・内容の記録
