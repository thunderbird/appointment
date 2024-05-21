terraform_binary              = "tofu"
terraform_version_constraint  = ">= 1.6.2"
terragrunt_version_constraint = ">= 0.55.15"


locals {
  project_vars = yamldecode(file("project_vars.yaml"))

  project     = local.project_vars.project
  short_name  = local.project_vars.short_name
  name_prefix = get_env("TF_VAR_name_prefix")
  region      = get_env("TF_VAR_region")

  tags = {
    project = local.project
    managed = "terragrunt"
  }

  parsed = regex(".*/environments/(?P<env>.*?)/.*", get_terragrunt_dir())
  env    = local.parsed.env
}

generate "backend" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  backend "s3" {
    bucket         = "${local.name_prefix}-state"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "${local.name_prefix}-locks"
  }
}
EOF
}
