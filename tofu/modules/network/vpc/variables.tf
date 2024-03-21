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

variable "vpc_cidr" {
  description = "CIDR block for appointment"
  type        = string
}
