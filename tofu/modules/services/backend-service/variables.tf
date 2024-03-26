variable "name_prefix" {
  description = "Prefix to be used with all resource names"
  type        = string
}

variable "subnets" {
  description = "Backend subnets"
  type        = list(any)
}

variable "region" {
  description = "Deployment region"
  type        = string
}

variable "log_group" {
  description = "ECS CLoudwatch log group"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
}

variable "target_group_arn" {
  description = "Backend ALB target group arn"
  type        = string
}

variable "ecs_cluster" {
  description = "Backend ECS cluster id"
  type = string
}

variable "security_group" {
  description = "Backend security group"
  type = string
}