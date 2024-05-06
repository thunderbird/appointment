variable "environment" {
  description = "Application environment ie. staging, production, etc..."
  type        = string
}

variable "name_prefix" {
  description = "Prefix to be used with all resource names"
  type        = string
}

variable "region" {
  description = "AWS deployment region"
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

variable "subnet_group" {
  description = "RDS subnet group"
  type        = string
}

variable "elasticache_security_group" {
  description = "Elasticache security group"
  type        = string
  default     = ""
}

variable "backend_security_group" {
  description = "Backend security group"
  type        = string
  default     = ""
}

variable "database_secret" {
  description = "Database secret"
  type        = string
  default     = ""
}