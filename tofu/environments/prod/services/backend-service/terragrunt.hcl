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
  environment = get_env("TF_VAR_environment")
  name_prefix = get_env("TF_VAR_name_prefix")
  region      = get_env("TF_VAR_region")
  //project          = include.root.locals.project
  //environment      = include.env.locals.environment
  short_name = include.root.locals.short_name
  //name_prefix      = "tb-${include.root.locals.short_name}-${include.env.locals.environment}"
  //region           = include.env.locals.region
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
  frontend_url        = get_env("frontend_url")   //"https://${local.project}.day"
  short_base_url      = get_env("short_base_url") //"https://${local.short_name}.day"
  app_env             = get_env("app_env")        //local.environment
  sentry_dsn          = get_env("sentry_dsn")     //"https://5dddca3ecc964284bb8008bc2beef808@o4505428107853824.ingest.sentry.io/4505428124827648"
  zoom_auth_callback  = get_env("zoom_callback")  //"https://${local.project}.day/api/v1/zoom/callback"
  short_name          = local.short_name
  database_secret     = dependency.database.outputs.db_secret
  db_enc_secret       = get_env("db_enc_secret")       //"arn:aws:secretsmanager:us-east-1:768512802988:secret:tb-apmt-production-db-secret-xcaWVh"
  smtp_secret         = get_env("smtp_secret")         //"arn:aws:secretsmanager:us-east-1:768512802988:secret:staging/appointment/socketlabs-UYmjaC"
  google_oauth_secret = get_env("google_oauth_secret") //"arn:aws:secretsmanager:us-east-1:768512802988:secret:tb-apmt-production-google-cal-oauth-8x5LUO"
  zoom_secret         = get_env("zoom_secret")         //"arn:aws:secretsmanager:us-east-1:768512802988:secret:staging/appointment/zoom-S862zi"
  fxa_secret          = get_env("fxa_secret")          //"arn:aws:secretsmanager:us-east-1:768512802988:secret:prod/appointment/fxa-lRA3qx"
  redis_endpoint      = dependency.cache.outputs.endpoint
  log_level           = get_env("log_level")
  tags                = local.tags
}