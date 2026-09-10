# A-2 構成図

<p align="center">
  <a href="https://raw.githubusercontent.com/moruku36/cloud-validation-level3-astra-light/main/experiments/A/A-2/architecture.jpg" target="_blank" title="クリックして高解像度・原寸大で拡大表示">
    <img src="architecture.jpg" alt="実験構成図: moruku36/cloud-validation-level3-astra-light (AWS構成)" width="100%" style="max-width: 1050px; border: 1px solid #e1e4e8; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
  </a>
  <br>
  <sub>🔍 <b>画像をタップ/クリックすると別タブで原寸大・高解像度表示されます</b></sub>
</p>

## 論理構成図 (Mermaid)

```mermaid
%%{init: {'themeVariables': { 'fontSize': '20px', 'fontFamily': 'ui-sans-serif, -apple-system, BlinkMacSystemFont, sans-serif' }}}%%
flowchart TB
  subgraph PublicLayer ["パブリックアクセス"]
    direction LR
    U["<b>👤 利用者 / クライアント</b>"]
    DNS["<b>🌐 Route 53</b><br/>DNSルーティング"]
    U -. DNS解決 .-> DNS
  end

  subgraph IngressLayer ["エントリ & セキュリティ"]
    direction LR
    WAF["<b>🛡️ AWS WAF (Regional)</b><br/>Rate Limit / 入力攻撃防御"]
    ALB["<b>⚖️ ALB (Load Balancer)</b><br/>HTTPS終端 / 2AZ負荷分散"]
    WAF ==>|検査後転送| ALB
  end

  subgraph TokyoVPC ["AWS 東京リージョン (本番VPC / 2AZ冗長)"]
    direction TB
    subgraph ComputeTier ["アプリケーション層 (常時2タスク並行)"]
      direction LR
      AppA["<b>🚀 ECS Fargate ARM (AZ-A)</b><br/>1vCPU / 2GB"]
      AppB["<b>🚀 ECS Fargate ARM (AZ-B)</b><br/>1vCPU / 2GB"]
    end

    subgraph DatabaseTier ["データストア層 (同期Multi-AZ)"]
      direction LR
      DB_Pri[("<b>🗄️ RDS PostgreSQL Primary</b><br/>AZ-A (gp3 50GB)")]
      DB_Stb[("<b>🗄️ RDS PostgreSQL Standby</b><br/>AZ-B (同期待機)")]
      DB_Pri <===>|同期レプリケーション<br/>(RPO=0)| DB_Stb
    end
  end

  subgraph ManagedAndDR ["付帯マネージドサービス & DR保管"]
    direction LR
    S3["<b>📦 S3 バケット (東京)</b><br/>画像保管・内部バックアップ"]
    Cognito["<b>🔑 Cognito Lite</b><br/>ユーザー認証"]
    SES["<b>✉️ SES 東京</b><br/>通知メール送信"]
    CW["<b>📊 CloudWatch</b><br/>毎分外形監視・アラーム"]
    DR_S3[("<b>🗾 S3 大阪バケット (DR)</b><br/>日次DBダンプ / 画像複製 (35日)")]
  end

  U ==>|HTTPS| WAF
  ALB -->|Private| AppA
  ALB -->|Private| AppB
  AppA -->|TLS| DB_Pri
  AppB -->|TLS| DB_Pri
  AppA & AppB -.-> S3 & Cognito & SES & CW
  S3 -.->|非同期クロスリージョン複製| DR_S3
  DB_Pri -.->|日次スナップショット転送| DR_S3
```

ALBからのみtask ingress許可。DB/S3は非公開。矢印は論理経路であり、AWS管理サービスの内部AZ構成を実測した図ではない。
