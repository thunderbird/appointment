#!/bin/env python3

import pulumi
import pulumi_cloudflare as cloudflare
import tb_pulumi
import tb_pulumi.cloudfront
import tb_pulumi.elasticache
import tb_pulumi.fargate
import tb_pulumi.network
import tb_pulumi.rds
import tb_pulumi.secrets

MSG_LB_MATCHING_CONTAINER = 'In this stack, container security groups must have matching load balancer security groups.'
MSG_LB_MATCHING_CLUSTER = 'In this stack, Fargate clusters must have matching load balancer security groups.'
MSG_CONTAINER_MATCHING_CLUSTER = 'In this stack, Fargate clusters must have matching container security groups.'

# Set up the project and easy access to a couple things
project = tb_pulumi.ThunderbirdPulumiProject()
resources = project.config.get('resources')
cloudflare_zone_id = project.pulumi_config.require_secret('cloudflare_zone_id')

# Create some private network space
vpc_opts = resources['tb:network:MultiCidrVpc'].get('appointment', {})
vpc = tb_pulumi.network.MultiCidrVpc(name=f'{project.name_prefix}-vpc', project=project, **vpc_opts)

# Copy secrets from Pulumi into AWS
secrets_managers = {
    name: tb_pulumi.secrets.PulumiSecretsManager(
        name=f'{project.name_prefix}-secrets',
        project=project,
        **config,
    )
    for name, config in resources.get('tb:secrets:PulumiSecretsManager', {}).items()
}

# Build security groups for load balancers
lb_sg_opts = resources.get('tb:network:SecurityGroupWithRules', {}).get('load_balancers', {})
lb_sgs = {
    service: tb_pulumi.network.SecurityGroupWithRules(
        name=f'{project.name_prefix}-sg-lb-{service}',
        project=project,
        vpc_id=vpc.resources['vpc'].id,
        opts=pulumi.ResourceOptions(depends_on=[vpc]),
        **sg,
    )
    if sg
    else None
    for service, sg in lb_sg_opts.items()
}

# Build security groups for containers
container_sgs = {}
for service, sg in resources['tb:network:SecurityGroupWithRules']['containers'].items():
    if service not in lb_sgs:
        raise ValueError(f'{MSG_LB_MATCHING_CONTAINER} Create a matching load_balancers entry for "{service}".')
    # Allow access from each load balancer to its respective container
    for rule in sg['rules']['ingress']:
        rule['source_security_group_id'] = lb_sgs[service].resources['sg'].id
    depends_on = [lb_sgs[service].resources['sg'], vpc] if lb_sgs[service] else []
    container_sgs[service] = tb_pulumi.network.SecurityGroupWithRules(
        name=f'{project.name_prefix}-sg-cont-{service}',
        project=project,
        vpc_id=vpc.resources['vpc'].id,
        opts=pulumi.ResourceOptions(depends_on=depends_on),
        **sg,
    )

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

# Create a memory cache for the backend containers to use
caches = {}
caches['backend'] = tb_pulumi.elasticache.ElastiCacheReplicationGroup(
    name=f'{project.name_prefix}-cache',
    project=project,
    subnets=vpc.resources.get('subnets', []),
    source_sgids=[container_sgs['backend'].resources['sg'].id],
    **resources.get('tb:elasticache:ElastiCacheReplicationGroup', {}).get('backend', {}),
)

redis_dns = cloudflare.DnsRecord(
    f'{project.name_prefix}-dns-redis',
    name=resources.get('domains', {}).get('redis', None),
    ttl=60,
    type='CNAME',
    zone_id=cloudflare_zone_id,
    content=caches['backend'].resources['replication_group'].primary_endpoint_address,
    proxied=False,
)

# Fargate Service
fargate_clusters = {}
for service, opts in resources['tb:fargate:FargateClusterWithLogging'].items():
    if service not in lb_sgs:
        raise ValueError(f'{MSG_LB_MATCHING_CLUSTER} Create a matching load_balancers entry for "{service}".')
    if service not in container_sgs:
        raise ValueError(f'{MSG_CONTAINER_MATCHING_CLUSTER} Create a matching load_balancers entry for "{service}".')
    lb_sg_ids = [lb_sgs[service].resources['sg'].id] if lb_sgs[service] else []
    depends_on = [
        container_sgs[service].resources['sg'],
        *vpc.resources['subnets'],
    ]
    if lb_sgs[service]:
        depends_on.append(lb_sgs[service].resources['sg'])
    fargate_clusters[service] = tb_pulumi.fargate.FargateClusterWithLogging(
        name=f'{project.name_prefix}-fargate-{service}',
        project=project,
        subnets=vpc.resources['subnets'],
        container_security_groups=[container_sgs[service].resources['sg'].id],
        load_balancer_security_groups=lb_sg_ids,
        opts=pulumi.ResourceOptions(depends_on=depends_on),
        **opts,
    )

# CloudFrontS3Service

# CF Function to rewrite requests
