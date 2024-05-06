include "root" {
  path   = find_in_parent_folders()
  expose = true
}

include "environment" {
  path   = find_in_parent_folders("environment.hcl")
  expose = true
}

terraform {
  source = "../../../../modules/services/backend-infra"
}

dependency "vpc" {
  config_path = "../../network/vpc"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan"]
  mock_outputs = {
    vpc_id                          = "mock_vpc_id"
    subnets                         = []
    private_subnets                 = []
    ecr_endpoint_security_group     = "mock_sg"
    secrets_endpoint_security_group = "mock_sg"
    logs_endpoint_security_group    = "mock_sg"
    database_subnet_cidrs           = ["10.0.1.0/24", "10.0.2.0/24"]
  }
}

locals {
  environment = include.environment.locals.environment
  name_prefix = "tb-${include.root.locals.short_name}-${include.environment.locals.environment}"
  region      = include.environment.locals.region

  project_tags     = include.root.locals.tags
  environment_tags = include.environment.locals.tags
  tags             = "${merge(local.project_tags, local.environment_tags)}"
}

inputs = {
  environment                     = local.environment
  name_prefix                     = local.name_prefix
  region                          = local.region
  vpc                             = dependency.vpc.outputs.vpc_id
  subnets                         = dependency.vpc.outputs.public_subnets
  ecr_endpoint_security_group     = dependency.vpc.outputs.ecr_endpoint_security_group
  secrets_endpoint_security_group = dependency.vpc.outputs.secrets_endpoint_security_group
  logs_endpoint_security_group    = dependency.vpc.outputs.logs_endpoint_security_group
  database_subnet_cidrs           = dependency.vpc.outputs.database_subnet_cidrs
  ssl_cert                        = "arn:aws:acm:us-east-1:768512802988:certificate/4a53e27b-0cd3-4855-a13f-5bac50015e43"
  tags                            = local.tags
}