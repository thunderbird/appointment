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

### cache

Contains the Elasticache redis cluster and supporting resources

### database

Contains the RDS database instance and supporting resources

### frontend

Contains the Cloudfront CDN distribution, frontend S3 bucket and supporting resources.  WHile the bucket contents will change with frontend code changes the infrastructure defined here will remain static

### backend-service

Contains the backend ECS service and task definitions.  This will be redeployed whenever the backend code is updated

## Deployment Order

All infrastructure should be deployed via terragrunt commands from the appropriate 'environments' folder.  Tofu should never be executed directly from the 'modules' folders

### Remote State

This is deployed individually before any other stacks and generally should not change with application or infrastructure deployments

1. tofu/environments/\<env>/terraform/tfbackend
   1. `cd tofu/environments/<env>/terraform/tfbackend`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`

### Infrastructure Stacks

These should be deployed in the following order and generally will only be updated with infrastructure changes while remaining static for code changes

1. tofu/environments/\<env>/network/vpc
   1. `cd tofu/environments/<env>/network/vpc`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
2. tofu/environments/\<env>/services/backend-infra
   1. `cd tofu/environments/<env>/services/backend-infra`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
3. tofu/environments/\<env>/data-store/cache
   1. `cd tofu/environments/<env>/datastore/cache`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
4. tofu/environments/\<env>/data-store/database
   1. `cd tofu/environments/<env>/data-store/database`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
5. tofu/environments/\<end>/services/frontend
   1. `cd tofu/environments/<env>/services/frontend`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`

### Application Stacks

1. tofu/environments/\<env>/services/backend-service
   1. `cd tofu/environments/<env>/services/backend-service`
   2. `terragrunt init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
