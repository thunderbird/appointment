variable "environment" {
  description = "Application environment ie. staging, production, etc..."
  type        = string
}

variable "name_prefix" {
  description = "Prefix to be used with all resource names"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
}

variable "region" {
  description = "AWS deployment region"
  type        = string
}

variable "ssl_cert" {
  description = "SSL certificate ARN in AWS Certificate Manager"
  type        = string
}

/*variable "urls" {
  description = "Site URLs"
  type        = list(any)
}*/

variable "backend_id" {
  description = "Backend id"
  type        = string
}

variable "backend_dns_name" {
  description = "Backend DNS name"
  type        = string
}

variable "frontend_bucket" {
  description = "Frontend S3 bucket"
  type        = string
}