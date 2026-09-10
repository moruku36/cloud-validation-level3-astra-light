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
flowchart LR
  subgraph Internet["パブリック / クライアント"]
    direction TB
    U["利用者 / ブラウザ"]
    DNS["Route 53 (DNS)"]
    U -. DNS解決 .-> DNS
  end

  subgraph Tokyo["AWS 東京リージョン (本番環境)"]
    direction TB
    subgraph Ingress["公開入口 & セキュリティ"]
      WAF["AWS WAF (Regional)"]
      ALB["ALB (HTTPS終端 / 2AZ負荷分散)"]
      WAF --> ALB
    end

    subgraph ComputeData["VPC 内部リソース (2AZ冗長)"]
      direction LR
      subgraph AZ_A["AZ-A 障害境界"]
        AppA["ECS Fargate ARM<br/>(1vCPU / 2GB)"]
        DB_Pri[("RDS PostgreSQL<br/>Primary (gp3 50GB)")]
      end
      subgraph AZ_B["AZ-B 障害境界"]
        AppB["ECS Fargate ARM<br/>(1vCPU / 2GB)"]
        DB_Stb[("RDS PostgreSQL<br/>Standby (同期待機)")]
      end
    end

    subgraph InternalServices["付帯マネージドサービス"]
      S3["S3 バケット (画像・内部バックアップ)"]
      Cognito["Cognito Lite (認証)"]
      SES["SES 東京 (メール送信)"]
      CW["CloudWatch (監視・アラーム)"]
      KMS["Secrets Manager / KMS"]
    end
  end

  subgraph Osaka["大阪リージョン (DR保管)"]
    DR_S3[("S3 大阪バケット<br/>(日次DB dump / 画像複製)")]
  end

  U ==>|HTTPS| WAF
  ALB -->|Private| AppA
  ALB -->|Private| AppB
  AppA -->|TLS| DB_Pri
  AppB -->|TLS| DB_Pri
  DB_Pri <===>|同期複製| DB_Stb
  AppA & AppB -.->|Gateway EP| S3
  AppA & AppB -.->|Private API| Cognito & SES & CW & KMS
  S3 -.->|非同期レプリケーション| DR_S3
  DB_Pri -.->|日次snapshot転送| DR_S3
```

ALBからのみtask ingress許可。DB/S3は非公開。矢印は論理経路であり、AWS管理サービスの内部AZ構成を実測した図ではない。
