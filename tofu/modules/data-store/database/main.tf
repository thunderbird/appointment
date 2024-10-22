locals {
  username = replace("${var.name_prefix}_user", "-", "_")
  secret = {

  }
}

resource "random_string" "secret_suffix" {
  length  = 8
  lower   = true
  numeric = false
  special = false
  upper   = true
}

module "db" {
  source = "github.com/terraform-aws-modules/terraform-aws-rds"

  identifier = var.name_prefix

  engine            = "mysql"
  engine_version    = "8.0.35"
  instance_class    = "db.t3.medium"
  allocated_storage = 20

  db_name                     = "appointment"
  username                    = local.username //jsondecode(data.aws_secretsmanager_secret_version.current.secret_string)["username"]
  password                    = random_password.db_password.result //jsondecode(data.aws_secretsmanager_secret_version.current.secret_string)["password"]
  manage_master_user_password = false
  port                        = "3306"

  iam_database_authentication_enabled = true

  multi_az               = var.environment == "production" ? true : false
  db_subnet_group_name   = var.subnet_group
  vpc_security_group_ids = [aws_security_group.rds.id]

  maintenance_window = "Wed:12:00-Wed:12:30"
  backup_window      = "03:00-06:00"

  enabled_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]

  create_db_subnet_group = true
  subnet_ids = var.database_subnets

  # DB parameter group
  family = "mysql8.0"

  # DB option group
  major_engine_version = "8.0"

  # Database Deletion Protection
  skip_final_snapshot = var.environment == "prod" ? false : true
  deletion_protection = var.environment == "prod" ? true : false

  parameters = [
    {
      name  = "require_secure_transport"
      value = 0
    }
  ]

  tags = var.tags
}

resource "aws_security_group" "rds" {
  name        = "${var.name_prefix}-rds"
  description = "Allow DB inbound traffic"
  vpc_id      = var.vpc
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-rds"
  })
}

resource "aws_vpc_security_group_ingress_rule" "allow_mysql_from_elasticache" {
  security_group_id            = aws_security_group.rds.id
  description                  = "Allow MySQL from elasticache"
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.elasticache_security_group
}

resource "aws_vpc_security_group_ingress_rule" "allow_mysql_from_backend" {
  security_group_id            = aws_security_group.rds.id
  description                  = "Allow MySQL from backend"
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.backend_security_group
}

resource "aws_secretsmanager_secret" "db_secret" {
  name = "${var.name_prefix}-db-${random_string.secret_suffix.result}"
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-db-${random_string.secret_suffix.result}"
  })
}

resource "aws_secretsmanager_secret_version" "db_secret_values" {
  secret_id = aws_secretsmanager_secret.db_secret.id
  secret_string = <<EOF
{
  "engine": "mysql",
  "username": "${local.username}",
  "password": "${random_password.db_password.result}",
  "host": "${module.db.db_instance_endpoint}",
  "dbname": "appointment",
  "port": "3306"
}
EOF
}

resource "random_password" "db_password" {
  length  = 32
  lower   = true
  numeric = true
  special = true
  upper   = true
}