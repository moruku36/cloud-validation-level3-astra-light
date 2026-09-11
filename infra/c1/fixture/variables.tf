variable "account_id" {
  type = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.account_id)) && !contains(concat([for n in range(10) : join("", [for i in range(12) : tostring(n)])], ["123456789012"]), var.account_id)
    error_message = "A confirmed dedicated account is required; placeholders are rejected."
  }
}
variable "experiment_id" {
  type = string
  validation {
    condition     = can(regex("^c1-[a-f0-9]{16}$", var.experiment_id))
    error_message = "Use a newly assigned c1- plus 16 hex nonce, never reuse an experiment."
  }
}
variable "operator_arn" {
  type = string
  validation {
    condition     = can(regex("^arn:aws:iam::[0-9]{12}:role/.+$", var.operator_arn))
    error_message = "Use the approved existing operator IAM role ARN, not a root/user/session."
  }
}
variable "expires_at" {
  type = string
  validation {
    condition     = can(formatdate("YYYY-MM-DD", var.expires_at))
    error_message = "An explicit RFC3339 expiry is required."
  }
}
variable "execution_authorized" {
  type    = bool
  default = false
}
locals {
  region       = "ap-northeast-1"
  prefix       = "${var.experiment_id}-${var.account_id}"
  backend_name = "${local.prefix}-state"
  fixture_name = "${local.prefix}-fixture"
  state_key    = "state/${var.experiment_id}/terraform.tfstate"
  tags         = { Experiment = var.experiment_id, ExpiresAt = var.expires_at, Purpose = "c1-cp1", OwnerRole = var.operator_arn }
}
