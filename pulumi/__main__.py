#!/bin/env python3

import pulumi
import pulumi_aws as aws
import tb_pulumi
#import tb_pulumi.cloudfront
#import tb_pulumi.fargate
import tb_pulumi.network
import tb_pulumi.rds
#import tb_pulumi.secrets
import urllib.parse

project = tb_pulumi.ThunderbirdPulumiProject()
resources = project.config.get('resources')

# Build the networking landscape
vpc_opts = resources['tb:network:MultiCidrVpc']['vpc']
vpc = tb_pulumi.network.MultiCidrVpc(
  f'{project.name_prefix}-vpc',
  project,
  **vpc_opts
)

# Build firewall rules
backend_sg_opts = resources['tb:network:SecurityGroupWithRules']['backend']
backend_sg = tb_pulumi.network.SecurityGroupWithRules(
  f'{project.name_prefix}-backend-sg',
  project,
  vpc_id=vpc.resources['vpc'].id,
  **backend_sg_opts,
  opts=pulumi.ResourceOptions(depends_on=vpc),
)
backend_alb_sg_opts = resources['tb:network:SecurityGroupWithRules']['backend-alb']
backend_alb_sg = tb_pulumi.network.SecurityGroupWithRules(
  f'{project.name_prefix}-backend-alb-sg',
  project,
  vpc_id=vpc.resources['vpc'].id,
  **backend_alb_sg_opts,
  opts=pulumi.ResourceOptions(depends_on=vpc),
)
cache_sg = tb_pulumi.network.SecurityGroup(
  f'{project.name_prefix}-cache-sg',
  project,
  vpc_id=vpc.resources['vpc'].id,
  opts=pulumi.ResourceOptions(depends_on=vpc),
)
db_sg = tb_pulumi.network.SecurityGroup(
  f'{project.name_prefix}-db-sg',
  project,
  vpc_id=vpc.resources['vpc'].id,
  opts=pulumi.ResourceOptions(depends_on=vpc),
)
backend_from_alb_rule_opts = resources['tb:network:SecurityGroupRule']['backend_ingress_from_alb']
backend_from_alb_rule_opts['config']['security_group_id'] = backend_sg.resources['sg'].id
backend_from_alb_rule_opts['config']['source_security_group_id'] = backend_alb_sg.resources['sg'].id
backend_from_alb_rule = tb_pulumi.network.SecurityGroupRule(
  f'{project.name_prefix}-backend-from-alb',
  project,
  **backend_from_alb_rule_opts,
  opts=pulumi.ResourceOptions(depends_on=[backend_sg, backend_alb_sg])
)
backend_to_db_rule_opts = resources['tb:network:SecurityGroupRule']['backend_egress_to_db']
backend_to_db_rule_opts['config']['security_group_id'] = backend_sg.resources['sg'].id
backend_to_db_rule_opts['config']['source_security_group_id'] = db_sg.resources['sg'].id
backend_to_db_rule = tb_pulumi.network.SecurityGroupRule(
  f'{project.name_prefix}-backend-to-db',
  project,
  **backend_to_db_rule_opts,
  opts=pulumi.ResourceOptions(depends_on=[backend_sg, db_sg])
)
backend_to_cache_rule_opts = resources['tb:network:SecurityGroupRule']['backend_egress_to_cache']
backend_to_cache_rule_opts['config']['security_group_id'] = backend_sg.resources['sg'].id
backend_to_cache_rule_opts['config']['source_security_group_id'] = cache_sg.resources['sg'].id
backend_to_cache_rule = tb_pulumi.network.SecurityGroupRule(
  f'{project.name_prefix}-backend-to-cache',
  project,
  **backend_to_cache_rule_opts,
  opts=pulumi.ResourceOptions(depends_on=[backend_sg, cache_sg])
)
backend_alb_to_backend_rule_opts = resources['tb:network:SecurityGroupRule']['backend_alb_egress_to_backend']
backend_alb_to_backend_rule_opts['config']['security_group_id'] = backend_alb_sg.resources['sg'].id
backend_alb_to_backend_rule_opts['config']['source_security_group_id'] = backend_sg.resources['sg'].id
backend_alb_to_backend_rule = tb_pulumi.network.SecurityGroupRule(
  f'{project.name_prefix}-backend_alb_to_backend',
  project,
  **backend_alb_to_backend_rule_opts,
  opts=pulumi.ResourceOptions(depends_on=[backend_alb_sg, backend_sg])
)
cache_from_backend_rule_opts = resources['tb:network:SecurityGroupRule']['cache_ingress_from_backend']
cache_from_backend_rule_opts['config']['security_group_id'] = cache_sg.resources['sg'].id
cache_from_backend_rule_opts['config']['source_security_group_id'] = backend_sg.resources['sg'].id
cache_from_backend_rule = tb_pulumi.network.SecurityGroupRule(
  f'{project.name_prefix}-cache_from_backend',
  project,
  **cache_from_backend_rule_opts,
  opts=pulumi.ResourceOptions(depends_on=[cache_sg, backend_sg])
)
cache_to_db_rule_opts = resources['tb:network:SecurityGroupRule']['cache_egress_to_db']
cache_to_db_rule_opts['config']['security_group_id'] = cache_sg.resources['sg'].id
cache_to_db_rule_opts['config']['source_security_group_id'] = db_sg.resources['sg'].id
cache_to_db_rule = tb_pulumi.network.SecurityGroupRule(
  f'{project.name_prefix}-cache_to_db',
  project,
  **cache_to_db_rule_opts,
  opts=pulumi.ResourceOptions(depends_on=[cache_sg, db_sg])
)
db_from_backend_rule_opts = resources['tb:network:SecurityGroupRule']['db_ingress_from_backend']
db_from_backend_rule_opts['config']['security_group_id'] = db_sg.resources['sg'].id
db_from_backend_rule_opts['config']['source_security_group_id'] = backend_sg.resources['sg'].id
db_from_backend_rule = tb_pulumi.network.SecurityGroupRule(
  f'{project.name_prefix}-db_from_backend',
  project,
  **db_from_backend_rule_opts,
  opts=pulumi.ResourceOptions(depends_on=[db_sg, backend_sg])
)
db_from_cache_rule_opts = resources['tb:network:SecurityGroupRule']['db_ingress_from_cache']
db_from_cache_rule_opts['config']['security_group_id'] = db_sg.resources['sg'].id
db_from_cache_rule_opts['config']['source_security_group_id'] = cache_sg.resources['sg'].id
db_from_cache_rule = tb_pulumi.network.SecurityGroupRule(
  f'{project.name_prefix}-db_from_cache',
  project,
  **db_from_cache_rule_opts,
  opts=pulumi.ResourceOptions(depends_on=[db_sg, cache_sg])
)

#rds_opts = resources['tb:rds:RdsDatabaseGroup']['database']
#rds = tb_pulumi.rds.RdsDatabaseGroup(
#  f'{project.name_prefix}-rds',
#  project,
#  vpc_id=vpc.resources['vpc'].id,
#  **rds_opts,
#  opts=pulumi.ResourceOptions(depends_on=vpc),
#)