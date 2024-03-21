output "id" {
  value = module.backend_alb.id
}

output "dns_name" {
  value = module.backend_alb.dns_name
}

output "security_group_id" {
  value = aws_security_group.backend.id
}