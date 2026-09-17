terraform {
  required_version = "= 1.13.5"
  required_providers { aws = { source = "hashicorp/aws", version = "= 6.14.1" } }
  backend "s3" {}
}
provider "aws" {
  region              = "ap-northeast-1"
  allowed_account_ids = [var.account_id]
  max_retries         = 1
  default_tags { tags = local.tags }
}
variable "kms_arn" {
  type = string
  validation {
    condition     = can(regex("^arn:aws:kms:ap-northeast-1:[0-9]{12}:key/[a-f0-9-]{36}$", var.kms_arn))
    error_message = "Bind the actual bootstrap key ARN."
  }
}
