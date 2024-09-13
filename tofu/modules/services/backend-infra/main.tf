data "aws_ec2_managed_prefix_list" "cloudfront" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}

data "aws_region" "current" {}

data "aws_prefix_list" "s3" {
  name = "com.amazonaws.${data.aws_region.current.name}.s3"
}

locals {
  target_group_key = "${var.name_prefix}-backend"
}

resource "random_string" "x_allow_value" {
  length  = 128
  lower   = true
  numeric = true
  special = true
  upper   = true
}

resource "random_string" "x_allow_suffix" {
  length  = 8
  lower   = true
  numeric = false
  special = false
  upper   = true
}
resource "aws_secretsmanager_secret" "x_allow_secret" {
  name = "${var.name_prefix}-x-allow-secret-${random_string.x_allow_suffix.result}"
}

resource "aws_secretsmanager_secret_version" "x_allow_secret_version" {
  secret_id     = aws_secretsmanager_secret.x_allow_secret.name
  secret_string = random_string.x_allow_value.result
}

module "ecs_cluster" {
  source = "github.com/terraform-aws-modules/terraform-aws-ecs/modules/cluster"

  cluster_name = var.name_prefix

  # Capacity provider
  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = 100
      }
    }
  }
  tags = var.tags
}

module "backend_alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

  name                = "${var.name_prefix}-backend"
  security_group_name = "${var.name_prefix}-backend-alb"

  load_balancer_type = "application"

  vpc_id  = var.vpc
  subnets = var.subnets

  enable_deletion_protection = var.environment == "production" ? true : false

  security_group_ingress_rules = {
    inbound_5000 = {
      from_port      = 5000
      to_port        = 5000
      ip_protocol    = "tcp"
      prefix_list_id = data.aws_ec2_managed_prefix_list.cloudfront.id
    },
    inbound_80 = {
      from_port   = 80
      to_port     = 80
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }

  security_group_egress_rules = {
    outbound = {
      from_port                    = 5000
      to_port                      = 5000
      ip_protocol                  = "tcp"
      referenced_security_group_id = aws_security_group.backend.id
    }
  }

  listeners = {

    https = {
      port            = 5000
      protocol        = "HTTPS"
      certificate_arn = var.ssl_cert
      fixed_response = {
        content_type = "text/plain"
        message_body = ""
        status_code  = 503
      }

      rules = {
        custom-header = {
          actions = [{
            type             = "forward"
            target_group_key = local.target_group_key
          }]
          conditions = [{
            http_header = {
              http_header_name = "X-Allow"
              values           = [random_string.x_allow_value.result]
            }
          }]
        }
      }
    },
    shortlink = {
      port     = 80
      protocol = "HTTP"

      redirect = {
        status_code = "HTTP_302"
        host        = trimprefix(var.frontend_url, "https://")
        path        = "/user/#{path}"
        port        = 443
        protocol    = "HTTPS"
      }
    }
  }

  target_groups = {
    "${local.target_group_key}" = {
      name                              = "${var.name_prefix}-backend"
      protocol                          = "HTTP"
      port                              = 5000
      target_type                       = "ip"
      deregistration_delay              = 5
      load_balancing_cross_zone_enabled = true

      health_check = {
        enabled             = true
        healthy_threshold   = 2
        interval            = 60
        matcher             = "200"
        path                = "/"
        port                = "traffic-port"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 2
      }

      # There's nothing to attach here in this definition. Instead,
      # ECS will attach the IPs of the tasks to this target group
      create_attachment = false
    }
  }
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-backend-alb"
  })
  security_group_tags = {
    Name = "${var.name_prefix}-backend-alb"
  }
}

resource "aws_security_group" "backend" {
  name        = "${var.name_prefix}-backend"
  description = "Appointment backend traffic"
  vpc_id      = var.vpc
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-backend"
  })
}

resource "aws_vpc_security_group_ingress_rule" "allow_5000_from_backend_alb" {
  security_group_id            = aws_security_group.backend.id
  description                  = "5000 from ALB"
  from_port                    = 5000
  to_port                      = 5000
  ip_protocol                  = "tcp"
  referenced_security_group_id = module.backend_alb.security_group_id
}

resource "aws_vpc_security_group_egress_rule" "allow_mysql_to_DB_subnets" {
  for_each          = toset(var.database_subnet_cidrs)
  security_group_id = aws_security_group.backend.id
  description       = "mysql to DB"
  from_port         = 3306
  to_port           = 3306
  ip_protocol       = "tcp"
  cidr_ipv4         = each.value
}

resource "aws_vpc_security_group_egress_rule" "allow_tls_to_ecr_endpoints" {
  security_group_id            = aws_security_group.backend.id
  description                  = "TLS to ECR endpoints"
  from_port                    = 443
  to_port                      = 443
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.ecr_endpoint_security_group
}

resource "aws_vpc_security_group_egress_rule" "allow_tls_to_logs_endpoint" {
  security_group_id            = aws_security_group.backend.id
  description                  = "TLS to logs endpoint"
  from_port                    = 443
  to_port                      = 443
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.logs_endpoint_security_group
}

resource "aws_vpc_security_group_egress_rule" "allow_tls_to_secrets_endpoint" {
  security_group_id            = aws_security_group.backend.id
  description                  = "TLS to secrets endpoint"
  from_port                    = 443
  to_port                      = 443
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.secrets_endpoint_security_group
}

resource "aws_vpc_security_group_egress_rule" "allow_tls_to_s3_endpoint" {
  security_group_id = aws_security_group.backend.id
  description       = "TLS to S3 endpoint"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  prefix_list_id    = data.aws_prefix_list.s3.id
}

resource "aws_vpc_security_group_egress_rule" "allow_tls_to_all" {
  security_group_id = aws_security_group.backend.id
  description       = "TLS to internet"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "allow_smtp_to_all" {
  security_group_id = aws_security_group.backend.id
  description       = "smtp to internet"
  from_port         = 587
  to_port           = 587
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}
