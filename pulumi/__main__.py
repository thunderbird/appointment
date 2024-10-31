#!/bin/env python3

import pulumi
import pulumi_aws as aws
import tb_pulumi
import tb_pulumi.cloudfront
import tb_pulumi.fargate
import tb_pulumi.network
import tb_pulumi.rds
import tb_pulumi.secrets
import urllib.parse

project = tb_pulumi.ThunderbirdPulumiProject()
resources = project.config.get('resources')

# Build the networking landscape
vpc_opts = resources['tb:network:MultiCidrVpc']['vpc']
vpc = tb_pulumi.network.MultiCidrVpc(f'{project.name_prefix}-vpc', project, **vpc_opts)