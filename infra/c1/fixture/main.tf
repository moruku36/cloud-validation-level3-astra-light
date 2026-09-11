resource "aws_s3_bucket" "fixture" {
  bucket        = local.fixture_name
  force_destroy = false
  lifecycle {
    precondition {
      condition     = var.execution_authorized && split(":", var.kms_arn)[4] == var.account_id && split(":", var.operator_arn)[4] == var.account_id
      error_message = "Execution approval and same-account binding are required."
    }
  }
}
resource "aws_s3_bucket_versioning" "fixture" {
  bucket = aws_s3_bucket.fixture.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_public_access_block" "fixture" {
  bucket                  = aws_s3_bucket.fixture.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_ownership_controls" "fixture" {
  bucket = aws_s3_bucket.fixture.id
  rule { object_ownership = "BucketOwnerEnforced" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "fixture" {
  bucket = aws_s3_bucket.fixture.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_arn
    }
    bucket_key_enabled = false
  }
}
resource "aws_s3_bucket_policy" "fixture" {
  bucket = aws_s3_bucket.fixture.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.fixture.arn, "${aws_s3_bucket.fixture.arn}/*"], Condition = { Bool = { "aws:SecureTransport" = "false" } } },
      { Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.fixture.arn, "${aws_s3_bucket.fixture.arn}/*"],
      Condition = { ArnNotEquals = { "aws:PrincipalArn" = concat([var.operator_arn], [for k in ["plan", "apply", "cleanup"] : "arn:aws:iam::${var.account_id}:role/${local.prefix}-${k}"]) } } },
      { Effect = "Deny", Principal = "*", Action = "s3:PutObject", Resource = "${aws_s3_bucket.fixture.arn}/*",
      Condition = { StringNotEqualsIfExists = { "s3:x-amz-server-side-encryption-aws-kms-key-id" = var.kms_arn } } }
    ]
  })
  depends_on = [aws_s3_bucket_public_access_block.fixture]
}
