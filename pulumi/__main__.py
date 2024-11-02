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
redis_sg_opts = resources['tb:network:SecurityGroupWithRules']['redis']
redis_sg = tb_pulumi.network.SecurityGroupWithRules(
  f'{project.name_prefix}-redis-sg',
  project,
  vpc_id=vpc.resources['vpc'].id,
  **redis_sg_opts,
  opts=pulumi.ResourceOptions(depends_on=vpc),
)
rds_sg_opts = resources['tb:network:SecurityGroupWithRules']['rds']
rds_sg = tb_pulumi.network.SecurityGroupWithRules(
  f'{project.name_prefix}-rds-sg',
  project,
  vpc_id=vpc.resources['vpc'].id,
  **rds_sg_opts,
  opts=pulumi.ResourceOptions(depends_on=vpc),
)
#rds_opts = resources['tb:rds:RdsDatabaseGroup']['database']
#rds = tb_pulumi.rds.RdsDatabaseGroup(
#  f'{project.name_prefix}-rds',
#  project,
#  vpc_id=vpc.resources['vpc'].id,
#  **rds_opts,
#  opts=pulumi.ResourceOptions(depends_on=vpc),
#)