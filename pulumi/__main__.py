#!/bin/env python3

import pulumi
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

project = tb_pulumi.ThunderbirdPulumiProject()

# Pull the "resources" config mapping
resources = project.config.get('resources')

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

# Fargate Service

# CloudFrontS3Service

# CF Function to rewrite requests
