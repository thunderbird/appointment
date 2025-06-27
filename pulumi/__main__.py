#!/bin/env python3

import pulumi
import pulumi_aws as aws
import pulumi_cloudflare as cloudflare
import tb_pulumi
import tb_pulumi.cloudfront
import tb_pulumi.elasticache
import tb_pulumi.fargate
import tb_pulumi.network
import tb_pulumi.rds
import tb_pulumi.secrets

from tb_pulumi.constants import (
    CLOUDFRONT_CACHE_POLICY_ID_DISABLED,
    CLOUDFRONT_CACHE_POLICY_ID_OPTIMIZED,
    CLOUDFRONT_ORIGIN_REQUEST_POLICY_ID_ALLVIEWER,
)

CLOUDFRONT_REWRITE_CODE_FILE = 'cloudfront-rewrite.js'
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

# Build a security group to allow traffic from containers into Redis
backend_cache_sg_opts = resources.get('tb:network:SecurityGroupWithRules', {}).get('other', {}).get('backend_cache', {})
backend_cache_sg_ingress_rules = backend_cache_sg_opts.get('rules', {}).get('ingress', {})
for rule in backend_cache_sg_ingress_rules:
    rule['source_security_group_id'] = container_sgs.get('backend').resources.get('sg').id
backend_cache_sg = tb_pulumi.network.SecurityGroupWithRules(
    name=f'{project.name_prefix}-sg-cache-backend',
    project=project,
    vpc_id=vpc.resources['vpc'].id,
    opts=pulumi.ResourceOptions(depends_on=depends_on),
    **backend_cache_sg_opts,
)

# Create the memory cache
backend_cache = aws.elasticache.ServerlessCache(
    f'{project.name_prefix}-cache-backend',
    security_group_ids=[backend_cache_sg.resources.get('sg').id],
    subnet_ids=[subnet.id for subnet in vpc.resources.get('subnets', {})],
    **resources.get('aws:elasticache:ServerlessCache', {}).get('backend', {}),
)
backend_cache_primary_endpoint = backend_cache.endpoints.apply(lambda endpoints: endpoints[0]['address'])
backend_cache_reader_endpoint = backend_cache.reader_endpoints.apply(lambda endpoints: endpoints[0]['address'])

redis_dns = cloudflare.DnsRecord(
    f'{project.name_prefix}-dns-redis',
    name=resources.get('domains', {}).get('redis', None),
    ttl=60,
    type='CNAME',
    zone_id=cloudflare_zone_id,
    content=backend_cache_primary_endpoint,
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

# Manage the CloudFront rewrite function; the code is managed in cloudfront-rewrite.js
rewrite_code = None
try:
    with open(CLOUDFRONT_REWRITE_CODE_FILE, 'r') as fh:
        rewrite_code = fh.read()
except IOError:
    pulumi.error(f'Could not read file {CLOUDFRONT_REWRITE_CODE_FILE}')

# CF Function to rewrite requests
cf_func = aws.cloudfront.Function(
    f'{project.name_prefix}-func-rewrite',
    code=rewrite_code,
    comment='Rewrites inbound requests to direct them to the Appointment backend API',
    name=f'{project.name_prefix}-rewrite',
    publish=True,
    runtime='cloudfront-js-2.0',
)
project.resources['cf_rewrite_function'] = cf_func

# Craft all the things we need for our CloudFront Distribution
backend_domain_name = fargate_clusters['backend'].resources['fargate_service_alb'].resources['albs']['backend'].dns_name
backend_origin_id = f'{project.name_prefix}-backend'
frontend_opts = resources.get('tb:cloudfront:CloudFrontS3Service', {}).get('frontend', {})
default_cache_behavior = {
        'allowed_methods': ['GET', 'HEAD'],
        'cached_methods': ['GET', 'HEAD'],
        'target_origin_id': f's3-{frontend_opts["service_bucket_name"]}',
        'cache_policy_id': CLOUDFRONT_CACHE_POLICY_ID_OPTIMIZED,
        'function_associations': [{'event_type': 'viewer-request', 'function_arn': cf_func.arn}],
        'viewer_protocol_policy': 'redirect-to-https',
    }
ordered_cache_behaviors = [
            {
                'path_pattern': '/api/*',
                'allowed_methods': ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH'],
                'cached_methods': ['GET', 'HEAD', 'OPTIONS'],
                'target_origin_id': backend_origin_id,
                'cache_policy_id': CLOUDFRONT_CACHE_POLICY_ID_DISABLED,
                'origin_request_policy_id': CLOUDFRONT_ORIGIN_REQUEST_POLICY_ID_ALLVIEWER,
                'function_associations': [{
                    'event_type': 'viewer-request',
                    'function_arn': cf_func.arn,
                }],
                'viewer_protocol_policy': 'redirect-to-https',
            }, {
                'path_pattern': '/fxa',
                'allowed_methods': ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH'],
                'cached_methods': ['GET', 'HEAD', 'OPTIONS'],
                'target_origin_id': backend_origin_id,
                'cache_policy_id': CLOUDFRONT_CACHE_POLICY_ID_DISABLED,
                'origin_request_policy_id': CLOUDFRONT_ORIGIN_REQUEST_POLICY_ID_ALLVIEWER,
                'function_associations': [{
                    'event_type': 'viewer-request',
                    'function_arn': cf_func.arn,
                }],
                'viewer_protocol_policy': 'redirect-to-https',
            },
        ]
if 'distribution' in frontend_opts:
    frontend_opts['distribution']['default_cache_behavior'] = default_cache_behavior
    frontend_opts['distribution']['ordered_cache_behaviors'] = ordered_cache_behaviors
else:
    frontend_opts['distribution'] = {
        'default_cache_behavior': default_cache_behavior,
        'ordered_cache_behaviors': ordered_cache_behaviors
    }

frontend = tb_pulumi.cloudfront.CloudFrontS3Service(
    name=f'{project.name_prefix}-frontend',
    project=project,
    # Add the backend service as an origin; the S3 bucket is automatically added by this module
    origins=[
        {
            'domain_name': backend_domain_name,
            'origin_id': backend_origin_id,
            'custom_origin_config': {
                'http_port': 80,
                'https_port': 5000,
                'origin_protocol_policy': 'https-only',
                'origin_ssl_protocols': ['TLSv1.2'],
            },
        }
    ],
    **frontend_opts,
    opts=pulumi.ResourceOptions(depends_on=[cf_func]),
)


# Monitoring

# CI
