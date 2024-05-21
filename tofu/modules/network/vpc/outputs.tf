output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "public_subnets" {
  value = module.vpc.public_subnets
}

output "database_subnets" {
  value = module.vpc.database_subnets
}

output "database_subnet_cidrs" {
  value = module.vpc.database_subnets_cidr_blocks
}

output "database_subnet_group" {
  value = module.vpc.database_subnet_group
}

output "ecr_endpoint_security_group" {
  value = aws_security_group.ecr_endpoint.id
}

output "secrets_endpoint_security_group" {
  value = aws_security_group.secrets_endpoint.id
}

output "logs_endpoint_security_group" {
  value = aws_security_group.logs_endpoint.id
}

output "ecs_execution_role" {
  value = module.ecs_task_execution_role.iam_role_arn
}