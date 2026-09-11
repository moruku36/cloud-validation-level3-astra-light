locals {
  backend_arn = aws_s3_bucket.state.arn
  fixture_arn = "arn:aws:s3:::${local.fixture_name}"
  state_arn   = "${local.backend_arn}/${local.state_key}"
  lock_arn    = "${local.state_arn}.tflock"
  bucket_read = ["s3:GetBucketLocation", "s3:GetBucketTagging", "s3:GetBucketVersioning", "s3:GetEncryptionConfiguration", "s3:GetBucketPublicAccessBlock", "s3:GetBucketOwnershipControls", "s3:GetBucketPolicy", "s3:GetBucketAcl", "s3:GetLifecycleConfiguration", "s3:GetBucketLogging", "s3:GetBucketObjectLockConfiguration", "s3:GetReplicationConfiguration", "s3:GetBucketWebsite", "s3:GetBucketCORS", "s3:GetAccelerateConfiguration", "s3:GetBucketRequestPayment"]
}
resource "aws_iam_role_policy" "experiment" {
  for_each = aws_iam_role.experiment
  name     = "cp1-scope"
  role     = each.value.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        { Effect = "Allow", Action = local.bucket_read, Resource = [local.backend_arn, local.fixture_arn] },
        { Effect = "Allow", Action = "s3:ListBucket", Resource = local.backend_arn,
        Condition = { StringLike = { "s3:prefix" = [local.state_key, "${local.state_key}.tflock", "env:/"] } } },
        { Effect = "Allow", Action = "s3:ListBucket", Resource = local.fixture_arn },
        { Effect = "Allow", Action = each.key == "plan" ? ["s3:GetObject"] : ["s3:GetObject", "s3:PutObject"], Resource = local.state_arn },
        { Effect = "Allow", Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"], Resource = local.lock_arn },
        { Effect = "Allow", Action = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey"], Resource = aws_kms_key.state.arn,
          Condition = { StringEquals = { "kms:ViaService" = "s3.ap-northeast-1.amazonaws.com" },
        StringLike = { "kms:EncryptionContext:aws:s3:arn" = ["${local.backend_arn}/*", "${local.fixture_arn}/*"] } } },
        { Effect = "Allow", Action = "kms:DescribeKey", Resource = aws_kms_key.state.arn }
      ],
      [for s in [
        { Effect = "Allow", Action = ["s3:CreateBucket", "s3:DeleteBucket", "s3:PutBucketTagging", "s3:PutBucketVersioning", "s3:PutEncryptionConfiguration", "s3:PutBucketPublicAccessBlock", "s3:PutBucketOwnershipControls", "s3:PutBucketPolicy", "s3:DeleteBucketPolicy"], Resource = local.fixture_arn },
        { Effect = "Allow", Action = ["s3:GetObject", "s3:PutObject"], Resource = "${local.fixture_arn}/synthetic/*" }
      ] : s if each.key == "apply"],
      [for s in [
        { Effect = "Deny", Action = ["s3:DeleteObject", "s3:DeleteObjectVersion"], NotResource = local.lock_arn },
        { Effect = "Deny", Action = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject"], NotResource = [local.state_arn, local.lock_arn, "${local.fixture_arn}/synthetic/*"] },
        { Effect = "Deny", Action = ["iam:*", "kms:ScheduleKeyDeletion", "kms:CancelKeyDeletion", "kms:PutKeyPolicy"], Resource = "*" }
      ] : s if each.key != "cleanup"],
      [for s in [
        { Effect = "Allow", Action = ["s3:ListBucket", "s3:ListBucketVersions", "s3:ListBucketMultipartUploads", "s3:DeleteBucket"], Resource = [local.backend_arn, local.fixture_arn] },
        { Effect = "Allow", Action = ["s3:GetObject", "s3:DeleteObject", "s3:DeleteObjectVersion", "s3:AbortMultipartUpload"], Resource = ["${local.backend_arn}/*", "${local.fixture_arn}/*"] },
        { Effect = "Allow", Action = ["kms:ScheduleKeyDeletion", "kms:ListResourceTags"], Resource = aws_kms_key.state.arn }
      ] : s if each.key == "cleanup"]
    )
  })
}
