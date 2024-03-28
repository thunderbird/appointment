include "root" {
  path   = find_in_parent_folders()
  expose = true
}

include "environment" {
  path   = find_in_parent_folders("environment.hcl")
  expose = true
}

terraform {
  source = "../../../../modules/data-store/database"
}

dependency "vpc" {
  config_path = "../../network/vpc"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan"]
  mock_outputs = {
    vpc_id                = "mock_vpc_id"
    database_subnet_group = "mock_subnet_group"

  }
}

dependency "cache" {
  config_path = "../cache"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan"]
  mock_outputs = {
    security_group_id = "mock_sg_id"
  }
}

dependency "backend" {
  config_path = "../../services/backend-infra"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan", "destroy"]
  mock_outputs = {
    security_group_id = "sg-mocksecuritygroup"
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
  environment                = local.environment
  name_prefix                = local.name_prefix
  region                     = local.region
  vpc                        = dependency.vpc.outputs.vpc_id
  subnet_group               = dependency.vpc.outputs.database_subnet_group
  elasticache_security_group = dependency.cache.outputs.security_group_id
  backend_security_group     = dependency.backend.outputs.security_group_id
  tags                       = local.tags
}