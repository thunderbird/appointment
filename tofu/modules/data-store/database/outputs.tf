output "db_instance_endpoint" {
  description = "The connection endpoint"
  value       = module.db.db_instance_endpoint
}

output "security_group" {
  description = "Database security group"
  value       = aws_security_group.rds.id
}

output "db_secret" {
  description = "Database Secret"
  value = aws_secretsmanager_secret_version.db_secret_values.arn
  sensitive = true
}