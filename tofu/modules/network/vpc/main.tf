locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}
################################################################################
# VPC Module
################################################################################

module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc"

  name = var.name_prefix
  cidr = var.vpc_cidr

  azs              = local.azs #initializes local.azs
  private_subnets  = [for k, v in local.azs : cidrsubnet("${var.vpc_cidr}", 8, k)]
  public_subnets   = [for k, v in local.azs : cidrsubnet("${var.vpc_cidr}", 8, k + 254)]
  database_subnets = [for k, v in local.azs : cidrsubnet("${var.vpc_cidr}", 8, k + 2)]

  create_database_subnet_group  = true
  manage_default_network_acl    = false
  manage_default_route_table    = false
  manage_default_security_group = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = false
  enable_vpn_gateway     = false

  enable_dhcp_options = false

  tags = var.tags
}

module "vpc_endpoints" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc/modules/vpc-endpoints"

  vpc_id = module.vpc.vpc_id

  create_security_group = false

  endpoints = {
    ecr_api = {
      service             = "ecr.api"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      policy              = data.aws_iam_policy_document.ecr_endpoint.json
      security_group_ids  = [aws_security_group.ecr_endpoint.id]
      tags = merge(var.tags, {
        Name = "${var.name_prefix}-ecr-api"
      })
    },
    ecr_dkr = {
      service             = "ecr.dkr"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      policy              = data.aws_iam_policy_document.ecr_endpoint.json
      security_group_ids  = [aws_security_group.ecr_endpoint.id]
      tags = merge(var.tags, {
        Name = "${var.name_prefix}-ecr-dkr"
      })
    },
    secrets_manager = {
      service             = "secretsmanager"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      policy              = data.aws_iam_policy_document.secrets_endpoint.json
      security_group_ids  = [aws_security_group.secrets_endpoint.id]
      tags = merge(var.tags, {
        Name = "${var.name_prefix}-secretsmanager"
      })
    },
    logs = {
      service             = "logs"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      policy              = data.aws_iam_policy_document.logs_endpoint.json
      security_group_ids  = [aws_security_group.logs_endpoint.id]
      tags = merge(var.tags, {
        Name = "${var.name_prefix}-logs"
      })
    },
    s3 = {
      service         = "s3"
      vpd_id          = module.vpc.vpc_id
      route_table_ids = module.vpc.private_route_table_ids
      tags = merge(var.tags, {
        Name = "${var.name_prefix}-s3"
      })
    }
  }
  tags = var.tags
}

# ECS Task Execution Role
module "ecs_task_execution_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"

  trusted_role_services = [
    "ecs-tasks.amazonaws.com"
  ]

  create_role = true

  role_name         = "${var.name_prefix}-ecs"
  role_description  = "ECS task execution role"
  role_requires_mfa = false

  custom_role_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    resource.aws_iam_policy.appointment_secrets_policy.arn,
    resource.aws_iam_policy.appointment_logs_policy.arn
  ]
  number_of_custom_role_policy_arns = 3
  tags                              = var.tags
}

resource "aws_iam_policy" "appointment_secrets_policy" {
  name        = "${var.name_prefix}-secrets"
  path        = "/"
  description = "Allow Appointment to access required secrets"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
              "arn:aws:secretsmanager:${var.region}:768512802988:secret:${var.environment}/appointment/*"
            ]
        }
    ]
}
EOF
  tags   = var.tags
}

resource "aws_iam_policy" "appointment_logs_policy" {
  name        = "${var.name_prefix}-logs"
  path        = "/"
  description = "Allow Appointment to create it's log group"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup"
            ],
            "Resource": [
              "arn:aws:logs:${var.region}:768512802988:log-group:/ecs/${var.name_prefix}:*"
            ]
        }
    ]
}
EOF
  tags   = var.tags
}

# ECR endpoint policy
data "aws_iam_policy_document" "ecr_endpoint" {
  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetAuthorizationToken"
    ]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = [module.ecs_task_execution_role.iam_role_arn]
    }
  }
}
# Secrets endpoint policy
data "aws_iam_policy_document" "secrets_endpoint" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecretVersionIds"
    ]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = [module.ecs_task_execution_role.iam_role_arn]
    }
  }
}
# Logs endpoint policy
data "aws_iam_policy_document" "logs_endpoint" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreatelogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = [module.ecs_task_execution_role.iam_role_arn]
    }
  }
}

# ECR Endpoint SG
resource "aws_security_group" "ecr_endpoint" {
  name        = "${var.name_prefix}-ecr"
  description = "Allow ECR inbound traffic"
  vpc_id      = module.vpc.vpc_id
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-ecr-endpoint"
  })
}

# Secrets endpoint SG
resource "aws_security_group" "secrets_endpoint" {
  name        = "${var.name_prefix}-secrets"
  description = "Allow Secrets Manager inbound traffic"
  vpc_id      = module.vpc.vpc_id
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-secrets-endpoint"
  })
}

# Logs endpoint SG
resource "aws_security_group" "logs_endpoint" {
  name        = "${var.name_prefix}-logs"
  description = "Allow Cloudwatch logs inbound traffic"
  vpc_id      = module.vpc.vpc_id
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-logs-endpoint"
  })
}
