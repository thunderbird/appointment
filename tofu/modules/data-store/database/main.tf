data "aws_secretsmanager_secret" "db_secrets" {
  arn = "arn:aws:secretsmanager:us-east-1:768512802988:secret:tb-apmt-stage-db-secret-V0syHj"
}
data "aws_secretsmanager_secret_version" "current" {
  secret_id = data.aws_secretsmanager_secret.db_secrets.id
}

module "db" {
  source = "github.com/terraform-aws-modules/terraform-aws-rds"

  identifier = var.name_prefix

  engine            = "mysql"
  engine_version    = "8.0.32"
  instance_class    = "db.t3.medium"
  allocated_storage = 20

  db_name                     = "appointment"
  username                    = jsondecode(data.aws_secretsmanager_secret_version.current.secret_string)["username"]
  password                    = jsondecode(data.aws_secretsmanager_secret_version.current.secret_string)["password"]
  manage_master_user_password = false
  port                        = "3306"

  iam_database_authentication_enabled = true

  multi_az               = var.environment == "production" ? true : false
  db_subnet_group_name   = var.subnet_group
  vpc_security_group_ids = [aws_security_group.rds.id]

  maintenance_window = "Wed:12:00-Wed:12:30"
  backup_window      = "03:00-06:00"

  enabled_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]

  # DB parameter group
  family = "mysql8.0"

  # DB option group
  major_engine_version = "8.0"

  # Database Deletion Protection
  skip_final_snapshot = true  #var.environment != "sandbox" ? false : true
  deletion_protection = false #var.environment != "sandbox" ? true : false

  parameters = [
    {
      name  = "require_secure_transport"
      value = 1
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