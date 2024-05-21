output "alb_id" {
  value = module.backend_alb.id
}

output "dns_name" {
  value = module.backend_alb.dns_name
}

output "security_group_id" {
  value = aws_security_group.backend.id
}

output "target_group_key" {
  value = local.target_group_key
}

output "target_group_arn" {
  value = module.backend_alb.target_groups["${local.target_group_key}"].arn
}

output "log_group" {
  value = module.ecs_cluster.cloudwatch_log_group_name
}

output "cluster_id" {
  value = module.ecs_cluster.id
}

output "x_allow_secret" {
  value = aws_secretsmanager_secret.x_allow_secret.name
  sensitive = true
}