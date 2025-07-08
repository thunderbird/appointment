#!/bin/env python3

import cloudfront
import pulumi
import tb_pulumi
import tb_pulumi.ci
import tb_pulumi.cloudfront
import tb_pulumi.cloudwatch
import tb_pulumi.elasticache
import tb_pulumi.fargate
import tb_pulumi.network
import tb_pulumi.rds
import tb_pulumi.secrets

from fargate import fargate
from redis import redis_cache
from security_groups import security_groups

#: Environments in which we should build a proxy for Posthog calls
POSTHOG_PROXY_STACKS = ['prod']

# Set up the project and easy access to a couple things
project = tb_pulumi.ThunderbirdPulumiProject()
resources = project.config.get('resources')
cloudflare_zone_id = project.pulumi_config.require_secret('cloudflare_zone_id')

# Create some private network space
vpc_opts = resources['tb:network:MultiCidrVpc'].get('appointment', {})
vpc = tb_pulumi.network.MultiCidrVpc(name=f'{project.name_prefix}-vpc', project=project, **vpc_opts)

# Build any EC2 instances we might need
instances = {
    name: tb_pulumi.ec2.SshableInstance(
        f'{project.name_prefix}-instance-{name}',
        project=project,
        subnet_id=vpc.resources['subnets'][0].id,
        vpc_id=vpc.resources['vpc'].id,
        opts=pulumi.ResourceOptions(depends_on=[vpc]),
        **config,
    )
    for name, config in resources.get('tb:ec2:SshableInstance').items()
}

# Copy secrets from Pulumi into AWS
secrets_managers = {
    name: tb_pulumi.secrets.PulumiSecretsManager(
        name=f'{project.name_prefix}-secrets',
        project=project,
        **config,
    )
    for name, config in resources.get('tb:secrets:PulumiSecretsManager', {}).items()
}

# Build security groups for load balancers, containers, and our Redis cache
backend_cache_sg, container_sgs, lb_sgs = security_groups(project=project, resources=resources, vpc=vpc)

# Create the Redis memory cache
backend_cache, cache_dns = redis_cache(project=project, security_group=backend_cache_sg, vpc=vpc, resources=resources)

# Fargate Service
fargate_clusters = fargate(
    container_security_groups=container_sgs,
    load_balancer_security_groups=lb_sgs,
    project=project,
    resources=resources,
    vpc=vpc,
)

# CloudFront function to handle request rewrites headed to the backend
rewrite_function = cloudfront.rewrite_function(project=project)

# Distribution to serve the frontend
frontend = cloudfront.frontend_distribution(
    backend_cluster=fargate_clusters.get('backend'),
    project=project,
    resources=resources,
    rewrite_function=rewrite_function,
)

# Distribution to proxy Posthog data through
# posthog_proxy = cloudfront.posthog_proxy()


# Monitoring
monitoring_opts = resources.get('tb:cloudwatch:CloudWatchMonitoringGroup', {}).get('cloudwatch', {})
monitoring = tb_pulumi.cloudwatch.CloudWatchMonitoringGroup(
    name=f'{project.name_prefix}-monitoring', project=project, **monitoring_opts
)

# CI
ci_opts = resources.get('tb:ci:AwsAutomationUser')
if ci_opts:
    automaton_opts = ci_opts.get('automaton')
    automaton = tb_pulumi.ci.AwsAutomationUser(
        name=f'{project.name_prefix}-automaton',
        project=project,
        **automaton_opts,
    )
