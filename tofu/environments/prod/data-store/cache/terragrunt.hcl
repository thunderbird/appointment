include "root" {
  path   = find_in_parent_folders()
  expose = true
}

include "environment" {
  path   = find_in_parent_folders("environment.hcl")
  expose = true
}

terraform {
  source = "../../../../modules/data-store/cache"
}

dependency "vpc" {
  config_path = "../../network/vpc"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan"]
  mock_outputs = {
    vpc_id                 = "mock_vpc_id"
    subnets                = ["subnet-mocksubnet1234567"]
    database_subnet_cidrs  = ["subnet-mocksubnet1234567"]
    source_security_groups = ["sg-mocksecuritygroup"]
  }
}

dependency "backend" {
  config_path = "../../services/backend-infra"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan", "destroy"]
  mock_outputs = {
    security_group_id = "mock_sg_id"
  }
}

locals {
  environment = get_env("TF_VAR_environment")
  name_prefix = get_env("TF_VAR_name_prefix")
  region      = get_env("TF_VAR_region")

  project_tags     = include.root.locals.tags
  environment_tags = include.environment.locals.tags
  tags             = "${merge(local.project_tags, local.environment_tags)}"
}

inputs = {
  name_prefix            = local.name_prefix
  vpc                    = dependency.vpc.outputs.vpc_id
  subnets                = dependency.vpc.outputs.database_subnets
  source_security_groups = [dependency.backend.outputs.security_group_id]
  database_subnet_cidrs  = dependency.vpc.outputs.database_subnet_cidrs
  tags                   = local.tags
}