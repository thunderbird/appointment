variable "name_prefix" {
  description = "Prefix to be used with all resource names"
  type        = string
}

variable "short_name" {
  description = "Application short name"
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
  type        = string
}

variable "security_group" {
  description = "Backend security group"
  type        = string
}

variable "image" {
  description = "Backend Docker image"
  type        = string
}

variable "task_execution_role" {
  description = "ECS task execution role"
  type        = string
}

variable "frontend_url" {
  description = "Frontend URL"
  type        = string
}

variable "short_base_url" {
  description = "Short base URL"
  type        = string
}

variable "app_env" {
  description = "Application environment (dev, stage, etc...)"
  type        = string
}

variable "sentry_dsn" {
  description = "Sentry DSN"
  type        = string
}

variable "zoom_auth_callback" {
  description = "Zoom authorization callback"
  type        = string
}

variable "database_secret" {
  description = "Database secret ARN"
  type        = string
}

variable "db_enc_secret" {
  description = "DB encryped secret ARN"
  type        = string
}

variable "smtp_secret" {
  description = "smtp connection info"
  type        = string
}

variable "google_oauth_secret" {
  description = "Google OAUTH secret ARN"
  type        = string
}

variable "zoom_secret" {
  description = "Zoom secret ARN"
  type        = string
}

variable "fxa_secret" {
  description = "FXA secret ARN"
  type        = string
}

variable "redis_endpoint" {
  description = "Redis cache endpoint"
  type = string
}

variable "log_level" {
  description = "application logging level"
  type = string
}