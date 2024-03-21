## Tooling
Code was written and tested with the following (these versions are enforced in code as minimums):
- OpenTofu v1.6.2
- Terragrunt 0.55.15
- hashicorp/aws v5.41.0

**Note:** All code should be run through Terragrunt, which will then execute the required Tofu commands
 
## Deployment Order

1. tofu/environments/\<env>/terraform/tfbackend
   1. `cd tofu/environments/<env>/terraform/tfbackend`
   2. `terragrun init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
2. tofu/environments/\<env>/network/vpc
   1. `cd tofu/environments/<env>/network/vpc`
   2. `terragrun init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
3. tofu/environments/\<env>/services/backend
   1. `cd tofu/environments/<env>/services/backend`
   2. `terragrun init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
4. tofu/environments/\<env>/data-store/cache
   1. `cd tofu/environments/<env>/datastore/cache`
   2. `terragrun init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
5. tofu/environments/\<env>/data-store/database
   1. `cd tofu/environments/<env>/data-store/database`
   2. `terragrun init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
6. tofu/environments/\<end>/services/frontend
   1. `cd tofu/environments/<env>/services/frontend`
   2. `terragrun init`
   3. `terragrunt validate`
   4. `terragrunt plan -out tfplan`
   5. `terragrunt apply tfplan`
