variable "name_prefix" {
  description = "Prefix to be used with all resource names"
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
  description = "subnets for elasticache"
  type        = list(any)
}

variable "source_security_groups" {
  description = "Security group IDs that can access the cache"
  type        = list(any)
}


