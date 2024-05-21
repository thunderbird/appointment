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

dependency "database" {
  config_path = "../../data-store/database"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan"]
  mock_outputs = {
    db_secret = "arn:aws:secretsmanager:us-east-1:768512802988:secret:mocksecretarn"
  }
}

dependency "cache" {
  config_path = "../../data-store/cache"

  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan"]
  mock_outputs = {
    redis_endpoint = "mockcache.serverless.use1.cache.amazonaws.com"
  }
}

locals {
  environment      = get_env("TF_VAR_environment")
  name_prefix      = get_env("TF_VAR_name_prefix")
  region           = get_env("TF_VAR_region")
  project          = include.root.locals.project
  short_name       = include.root.locals.short_name
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
  frontend_url        = get_env("TF_VAR_frontend_url")
  short_base_url      = get_env("TF_VAR_short_base_url")
  app_env             = get_env("TF_VAR_app_env")
  sentry_dsn          = get_env("TF_VAR_sentry_dsn")
  zoom_auth_callback  = get_env("TF_VAR_zoom_callback")
  short_name          = local.short_name
  database_secret     = dependency.database.outputs.db_secret
  db_enc_secret       = get_env("TF_VAR_db_enc_secret")
  smtp_secret         = get_env("TF_VAR_smtp_secret")
  google_oauth_secret = get_env("TF_VAR_google_oauth_secret")
  zoom_secret         = get_env("TF_VAR_zoom_secret")
  fxa_secret          = get_env("TF_VAR_fxa_secret")
  log_level           = get_env("TF_VAR_log_level")
  redis_endpoint      = dependency.cache.outputs.endpoint
  tags                = local.tags
}