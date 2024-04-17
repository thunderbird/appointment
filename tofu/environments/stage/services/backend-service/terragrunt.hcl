include "root" {
  path   = find_in_parent_folders()
  expose = true
}

include "env" {
  path   = find_in_parent_folders("environment.hcl")
  expose = true
}

terraform {
  source = "../../../../modules/services/backend-service"
}

dependency "vpc" {
  config_path = "../../network/vpc"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan"]
  mock_outputs = {
    private_subnets    = ["subnet-mocksubnet1234567"]
    ecs_execution_role = "arn:aws:iam::768512802988:role/mockrolearn"
  }
}

dependency "backend-infra" {
  config_path = "../backend-infra"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan"]
  mock_outputs = {
    target_group_arn  = "arn:aws:elasticloadbalancing:us-east-1:768512802988:targetgroup/mocktg/12345678901234"
    log_group         = "MOCK_LOGS"
    cluster_id        = "MOCK_CLUSTER_ID"
    security_group_id = "MOCK_SG"
  }
}

locals {
  environment      = include.env.locals.environment
  name_prefix      = "tb-${include.root.locals.short_name}-${include.env.locals.environment}"
  region           = include.env.locals.region
  project_tags     = include.root.locals.tags
  environment_tags = include.env.locals.tags
  tags             = "${merge(local.project_tags, local.environment_tags)}"
}

inputs = {
  name_prefix         = local.name_prefix
  region              = local.region
  subnets             = dependency.vpc.outputs.private_subnets
  log_group           = dependency.backend-infra.outputs.log_group
  target_group_arn    = dependency.backend-infra.outputs.target_group_arn
  security_group      = dependency.backend-infra.outputs.security_group_id
  ecs_cluster         = dependency.backend-infra.outputs.cluster_id
  task_execution_role = dependency.vpc.outputs.ecs_execution_role
  tags                = local.tags
}