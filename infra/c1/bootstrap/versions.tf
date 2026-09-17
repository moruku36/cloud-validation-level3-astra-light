terraform {
  required_version = "= 1.13.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "= 6.14.1" }
  }
  backend "local" {}
}
provider "aws" {
  region              = "ap-northeast-1"
  allowed_account_ids = [var.account_id]
  max_retries         = 1
  default_tags { tags = local.tags }
}
