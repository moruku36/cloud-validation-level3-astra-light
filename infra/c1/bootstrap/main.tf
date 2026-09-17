resource "aws_kms_key" "state" {
  description             = "CP1 isolated state encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = false
  multi_region            = false
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Sid = "ExistingOperatorOnly", Effect = "Allow", Principal = { AWS = var.operator_arn }, Action = "kms:*", Resource = "*" },
      { Sid      = "ScopedIAMDelegation", Effect = "Allow", Principal = { AWS = "arn:aws:iam::${var.account_id}:root" },
        Action   = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey", "kms:ScheduleKeyDeletion"],
        Resource = "*", Condition = { ArnEquals = { "aws:PrincipalArn" = [for k in ["plan", "apply", "cleanup"] : "arn:aws:iam::${var.account_id}:role/${local.prefix}-${k}"] } }
      }
    ]
  })
  lifecycle {
    prevent_destroy = true
    precondition {
      condition     = var.execution_authorized && split(":", var.operator_arn)[4] == var.account_id
      error_message = "No execution approval, or operator belongs to another account."
    }
  }
}
resource "aws_s3_bucket" "state" {
  bucket        = local.backend_name
  force_destroy = false
  lifecycle {
    prevent_destroy = true
    precondition {
      condition     = var.execution_authorized && split(":", var.operator_arn)[4] == var.account_id
      error_message = "Explicit execution authorization required."
    }
  }
}
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_ownership_controls" "state" {
  bucket = aws_s3_bucket.state.id
  rule { object_ownership = "BucketOwnerEnforced" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.state.arn
    }
    bucket_key_enabled = false
  }
}
resource "aws_s3_bucket_policy" "state" {
  bucket = aws_s3_bucket.state.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.state.arn, "${aws_s3_bucket.state.arn}/*"], Condition = { Bool = { "aws:SecureTransport" = "false" } } },
      { Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.state.arn, "${aws_s3_bucket.state.arn}/*"],
      Condition = { ArnNotEquals = { "aws:PrincipalArn" = concat([var.operator_arn], [for r in aws_iam_role.experiment : r.arn]) } } },
      { Effect = "Deny", Principal = "*", Action = ["s3:PutObject"], Resource = "${aws_s3_bucket.state.arn}/*",
      Condition = { StringNotEqualsIfExists = { "s3:x-amz-server-side-encryption-aws-kms-key-id" = aws_kms_key.state.arn } } }
    ]
  })
  depends_on = [aws_s3_bucket_public_access_block.state]
}
resource "aws_iam_role" "experiment" {
  depends_on           = [aws_kms_key.state]
  for_each             = toset(["plan", "apply", "cleanup"])
  name                 = "${local.prefix}-${each.key}"
  max_session_duration = 3600
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { AWS = var.operator_arn }, Action = "sts:AssumeRole" }]
  })
}
output "binding" {
  value = {
    account_id     = var.account_id, region = local.region, experiment_id = var.experiment_id,
    backend_bucket = aws_s3_bucket.state.id, fixture_bucket = local.fixture_name,
    state_key      = local.state_key, kms_arn = aws_kms_key.state.arn,
    roles          = { for k, v in aws_iam_role.experiment : k => v.arn }
  }
  sensitive = true
}
