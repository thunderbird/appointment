locals {
  environment_vars = yamldecode(file("environment_vars.yaml"))

  environment = local.environment_vars.environment
  region      = local.environment_vars.region

  tags = {
    environment = local.environment
  }
}

generate "versions" {
  path      = "versions_override.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
    terraform {
      required_providers {
        aws = {
          source = "hashicorp/aws"
          version = ">= 5.46.0"
        }
        random = {
          source = "hashicorp/random"
          version = ">= 3.6.1"
        }
      }
    }
EOF
}