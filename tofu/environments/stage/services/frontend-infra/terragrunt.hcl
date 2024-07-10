include "root" {
  path   = find_in_parent_folders()
  expose = true
}

include "environment" {
  path   = find_in_parent_folders("environment.hcl")
  expose = true
}

terraform {
  source = "../../../../modules/services/frontend-infra"
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
  environment = get_env("TF_VAR_environment")
  name_prefix = get_env("TF_VAR_name_prefix")
  region      = get_env("TF_VAR_region")

  project_tags     = include.root.locals.tags
  environment_tags = include.environment.locals.tags
  tags             = "${merge(local.project_tags, local.environment_tags)}"
}

inputs = {
  environment      = local.environment
  name_prefix      = local.name_prefix
  region           = local.region
  tags             = local.tags
  ssl_cert         = get_env("TF_VAR_ssl_cert_arn")
  backend_id       = dependency.backend.outputs.alb_id
  backend_dns_name = dependency.backend.outputs.dns_name
  x_allow_secret   = dependency.backend.outputs.x_allow_secret
  frontend_url     = get_env("TF_VAR_frontend_url")
}