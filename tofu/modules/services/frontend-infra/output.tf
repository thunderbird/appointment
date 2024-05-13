output "bucket" {
  value = aws_s3_bucket.frontend.bucket_domain_name
}

output "bucket_name" {
  value = aws_s3_bucket.frontend.id
}

output "cloudfront_arn" {
  value = aws_cloudfront_distribution.appointment.arn
}
