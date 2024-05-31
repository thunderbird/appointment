# Tooling

Code was written and tested with the following (these versions are enforced in code as minimums):

- OpenTofu v1.6.2
- Terragrunt 0.55.15
- hashicorp/aws v5.46.0
- hashicorp/random v3.6.1

**Note:** All code should be run through Terragrunt, which will then execute the required Tofu commands

## Modules

### tfbackend

Contains the remote state resources:

- S3 bucket - state
- DynamoDB - locks

### vpc

Contains the VPC and all core network resources and supporting security groups etc...including:

- subnets
- vpc endpoints
- IGW
- NAT gateways

### backend-infra

Contains the ECS cluster & Application Load Balancer for the backend & supporting resources

- ECS cluster
- application load balancer
- security group

### cache

Contains the Elasticache redis cluster and supporting resources

- Elasticache serverless Redis cache
- security group

### database

Contains the RDS database instance and supporting resources

- RDS mysql database
- security group

### frontend-infra

Contains the Cloudfront CDN distribution, frontend S3 bucket and supporting resources.  WHile the bucket contents will change with frontend code changes the infrastructure defined here will remain static

- S3 bucket
- Cloudfront distribution
- Cloudfront function

### backend-service

Contains the backend ECS service and task definitions.  This will be redeployed whenever the backend code is updated

- ECS service
- ECS task definition

## Deployment Order

All infrastructure should be deployed via terragrunt commands from the appropriate 'environments' folder.  Tofu should never be executed directly from the 'modules' folders

### Remote State

This is deployed individually before any other stacks and generally should not change with application or infrastructure deployments.  For the initial run in a new environment comment out the "generate "backend" block in tofu/environments/terragrunt.hcl.  This is required to created the backend S3 state bucket and DynamoDB lock table.

1. tofu/environments/\<env>/terraform/tfbackend
   1. `cd tofu/environments/<env>/terraform/tfbackend`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`

### Infrastructure Stacks

These should be deployed in the following order and generally will only be updated with infrastructure changes while remaining static for code changes.  The Tofu files pull some information from environment variables.  When Github Actions workflows are run these are populated by Github environment/repository variables.  When running terragrunt commands locally the specified environment variables must be set/

1. tofu/environments/\<env>/network/vpc
   Required Environment Variables:
    - TF_VAR_name_prefix
    - TF_VAR_environment
    - TF_VAR_region

   1. `cd tofu/environments/<env>/network/vpc`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
2. tofu/environments/\<env>/services/backend-infra
   Required Environment Variables:
    - TF_VAR_name_prefix
    - TF_VAR_environment
    - TF_VAR_region
    - TF_VAR_frontend_url

   1. `cd tofu/environments/<env>/services/backend-infra`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
3. tofu/environments/\<env>/data-store/cache
   Required Environment Variables:
    - TF_VAR_name_prefix
    - TF_VAR_environment
    - TF_VAR_region

   1. `cd tofu/environments/<env>/datastore/cache`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
4. tofu/environments/\<env>/data-store/database
   Required Environment Variables:
    - TF_VAR_name_prefix
    - TF_VAR_environment
    - TF_VAR_region

   1. `cd tofu/environments/<env>/data-store/database`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
5. tofu/environments/\<end>/services/frontend-infra
   Required Environment Variables:
    - TF_VAR_name_prefix
    - TF_VAR_environment
    - TF_VAR_region

   1. `cd tofu/environments/<env>/services/frontend-infra`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`

### Application Stacks

#### Backend

The application backend is deployed as an ECS service via terragrunt

1. tofu/environments/\<env>/services/backend-service
   Required Environment Variables:
    - TF_VAR_name_prefix
    - TF_VAR_environment
    - TF_VAR_region
    - TF_VAR_name_frontend_url
    - TF_VAR_short_base_url
    - TF_VAR_app_env
    - TF_VAR_sentry_dsn
    - TF_VAR_zoom_callback
    - TF_VAR_db_enc_secret
    - TF_VAR_smtp_secret
    - TF_VAR_google_oauth_secret
    - TF_VAR_zoom_secret
    - TF_VAR_fxa_secret
    - TF_VAR_log_level

   1. `cd tofu/environments/<env>/services/backend-service`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`

#### Frontend

The application frontend is deployed to an S3 bucket fronted by Cloudfront.  As such it can be deployed by uploadingx files to S3 and creating a Cloudfront invalidation.

- aws s3 sync frontend/dist \<Appointment Environment Frontend S3 Bucket URI>
- aws cloudfront create-invalidation --distribution-id \<Appointment Environment Cloudfront Distribution ID> --paths "/*"
