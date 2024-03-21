locals {
  environment_vars = yamldecode(file("environment_vars.yaml"))

  environment = local.environment_vars.environment
  region      = local.environment_vars.region

  tags = {
    environment = local.environment
  }
}