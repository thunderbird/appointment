# S3 Bucket
locals {
  bucket     = "${var.name_prefix}-frontend"
  log_bucket = "${var.name_prefix}-frontend-logs"
}

resource "aws_s3_bucket" "frontend" {
  bucket = local.bucket

  force_destroy = true

  tags = merge(var.tags, {
    Name = local.bucket
  })
}

resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.bucket
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "allow_access_from_cloudfront" {
  bucket = aws_s3_bucket.frontend.id
  policy = data.aws_iam_policy_document.allow_access_from_cloudfront.json
}

data "aws_iam_policy_document" "allow_access_from_cloudfront" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.frontend.arn}/*"
    ]

    condition {
      test     = "StringLike"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.appointment.arn]
    }
  }
}

# Cloudfront Distribution
data "aws_cloudfront_cache_policy" "CachingDisabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_cache_policy" "CachingOptimized" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_origin_request_policy" "AllViewer" {
  name = "Managed-AllViewer"
}

data "aws_secretsmanager_secret_version" "x_allow_value" {
  secret_id = var.x_allow_secret
}

resource "aws_cloudfront_distribution" "appointment" {
  comment = "appointment ${var.environment} frontend"
  enabled = true

  aliases = [trimprefix(var.frontend_url, "https://")]

  logging_config {
    bucket          = "${aws_s3_bucket.request_logs.id}.s3.amazonaws.com"
    include_cookies = true
  }

  origin {
    origin_id                = "${var.name_prefix}-frontend"
    domain_name              = aws_s3_bucket.frontend.bucket_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
  }

  origin {
    origin_id   = var.backend_id
    domain_name = var.backend_dns_name
    custom_origin_config {
      http_port              = 80
      https_port             = 5000
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    custom_header {
      name  = "X-Allow"
      value = data.aws_secretsmanager_secret_version.x_allow_value.secret_string
    }
  }

  #aliases = var.urls

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "${var.name_prefix}-frontend"

    cache_policy_id = data.aws_cloudfront_cache_policy.CachingOptimized.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.rewrite.arn
    }

    viewer_protocol_policy = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = var.backend_id

    cache_policy_id          = data.aws_cloudfront_cache_policy.CachingDisabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.AllViewer.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.rewrite.arn
    }

    viewer_protocol_policy = "redirect-to-https"

  }

  ordered_cache_behavior {
    path_pattern     = "/fxa"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = var.backend_id

    cache_policy_id          = data.aws_cloudfront_cache_policy.CachingDisabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.AllViewer.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.rewrite.arn
    }

    viewer_protocol_policy = "redirect-to-https"

  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn            = var.ssl_cert
    cloudfront_default_certificate = false
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2021"
  }
}

resource "aws_cloudfront_origin_access_control" "oac" {
  name                              = "${var.name_prefix}-frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_function" "rewrite" {
  name    = "${var.name_prefix}-rewrite"
  runtime = "cloudfront-js-2.0"
  code    = <<EOT
  async function handler(event) {
    const request = event.request;
    const apiPath = "/api/v1";
    const ignorePaths = ['/fxa', '/assets', '/appointment_logo.svg'];
    const pathCheckFn = (path) => request.uri.startsWith(path);

    // If our api path is the first thing that's found in the uri then remove it from the uri.
    if (request.uri.indexOf(apiPath) === 0) {
      request.uri = request.uri.replace(apiPath, "");
    } else if (!ignorePaths.some(pathCheckFn)) {
      // If we're not in one of the ignorePaths then force them to /index.html
      request.uri = '/index.html';
    }
    // else carry on like normal.
    return request;
  }
  EOT
}

resource "aws_s3_bucket" "request_logs" {
  bucket        = local.log_bucket
  force_destroy = true

  tags = merge(var.tags, {
    Name = "${local.bucket}-request-logs"
  })
}

resource "aws_s3_bucket_versioning" "request_logs" {
  bucket = aws_s3_bucket.request_logs.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "request_logs" {
  bucket = aws_s3_bucket.request_logs.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "request_logs" {
  bucket                  = aws_s3_bucket.request_logs.bucket
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "request_logs" {
  bucket = aws_s3_bucket.request_logs.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "request_logs" {
  depends_on = [aws_s3_bucket_ownership_controls.request_logs]
  bucket     = aws_s3_bucket.request_logs.id
  acl        = "private"
}