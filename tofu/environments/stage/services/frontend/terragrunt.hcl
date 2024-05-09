include "root" {
  path   = find_in_parent_folders()
  expose = true
}

include "environment" {
  path   = find_in_parent_folders("environment.hcl")
  expose = true
}

terraform {
  source = "../../../../modules/services/frontend"
}

dependency "backend" {
  config_path = "../../services/backend-infra"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan", "destroy"]
  mock_outputs = {
    alb_id         = "mock_alb_id"
    dns_name       = "mock_dns_name"
    x_allow_secret = "mock_secret"
  }
}

locals {
  environment = get_env("environment")
  name_prefix = get_env("name_prefix")
  region      = get_env("region")

  project_tags     = include.root.locals.tags
  environment_tags = include.environment.locals.tags
  tags             = "${merge(local.project_tags, local.environment_tags)}"


  ssl_cert = "arn:aws:acm:us-east-1:768512802988:certificate/4a53e27b-0cd3-4855-a13f-5bac50015e43"
}

inputs = {
  environment      = local.environment
  name_prefix      = local.name_prefix
  region           = local.region
  tags             = local.tags
  ssl_cert         = local.ssl_cert
  backend_id       = dependency.backend.outputs.alb_id
  backend_dns_name = dependency.backend.outputs.dns_name
  x_allow_secret   = dependency.backend.outputs.x_allow_secret
}