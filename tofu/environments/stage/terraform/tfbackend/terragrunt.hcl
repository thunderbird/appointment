include "root" {
  path   = find_in_parent_folders()
  expose = true
}

include "environment" {
  path   = find_in_parent_folders("environment.hcl")
  expose = true
}

terraform {
  source = "../../../../modules/terraform/tfbackend"
}

locals {
  bucket_name = "tb-${include.root.locals.short_name}-${include.environment.locals.environment}-state"
  table_name  = "tb-${include.root.locals.short_name}-${include.environment.locals.environment}-locks"

  project_tags     = include.root.locals.tags
  environment_tags = include.environment.locals.tags
  tags             = "${merge(local.project_tags, local.environment_tags)}"
}

inputs = {
  bucket_name = local.bucket_name
  table_name  = local.table_name
  tags        = local.tags
}