variable "aws_region" {
  type        = string
  description = "AWS deployment region (strictly within Japan)"
  default     = "ap-northeast-1"
}

variable "env" {
  type        = string
  description = "Environment identifier (e.g. c1-low, c3-high)"
  default     = "c-val"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR"
  default     = "10.10.0.0/16"
}

variable "azs" {
  type        = list(string)
  description = "Target availability zones"
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "is_high_tier" {
  type        = bool
  description = "True for H tier (2AZ Multi-AZ RDS, 2 tasks), False for L tier (Single-AZ, 1 task)"
  default     = false
}
