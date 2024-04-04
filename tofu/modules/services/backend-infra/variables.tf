variable "environment" {
  description = "Application environment ie. staging, production, etc..."
  type        = string
}

variable "name_prefix" {
  description = "Prefix to be used with all resource names"
  type        = string
}

variable "region" {
  description = "Deployment region"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
}

variable "vpc" {
  description = "VPC ID"
  type        = string
}

variable "subnets" {
  description = "Backend subnets"
  type        = list(any)
}

variable "ecr_endpoint_security_group" {
  description = "ECR API & DKS VPC endpoint security group"
  type        = string
}

variable "secrets_endpoint_security_group" {
  description = "Secrets Manager VPC endpoint security group"
  type        = string
}

variable "logs_endpoint_security_group" {
  description = "Cloudwatch logs VPC endpoint security group"
  type        = string
}

variable "database_subnet_cidrs" {
  description = "Database subnet CIDRs"
  type        = list
}

variable "backend_image" {
  description = "Backend image ECR URI"
  type = string
  default = "public.ecr.aws/amazonlinux/amazonlinux:minimal"
}

variable "ssl_cert" {
  description = "SSL certificate ARN in AWS Certificate Manager"
  type        = string
}