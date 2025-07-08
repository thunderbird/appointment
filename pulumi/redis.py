import pulumi_aws as aws
import pulumi_cloudflare as cloudflare

from tb_pulumi import ThunderbirdPulumiProject
from tb_pulumi.network import MultiCidrVpc, SecurityGroupWithRules


def redis_cache(
    project: ThunderbirdPulumiProject,
    security_group: SecurityGroupWithRules,
    resources: dict,
    vpc: MultiCidrVpc,
):
    """
    Builds a Redis cache.

    :param project: The project to store all the resources in.
    :type project: ThunderbirdPulumiProject

    :param security_group: The security group to apply to the cache.
    :type security_group: SecurityGroupWithRules

    :param resources: The full set of configured resources.
    :type resources: dict

    :param vpc: The VPC to build the cache in.
    :type vpc: MultiCidrVpc

    :return: Tuple with two values:
        - The pulumi_aws.elasticache.ServerlessCache resource
        - The pulumi_cloudflare.DnsRecord resource pointing to the cache
    :rtype: _type_
    """
    cloudflare_zone_id = project.pulumi_config.require_secret('cloudflare_zone_id')
    backend_cache = aws.elasticache.ServerlessCache(
        f'{project.name_prefix}-cache-backend',
        security_group_ids=[security_group.resources.get('sg').id],
        subnet_ids=[subnet.id for subnet in vpc.resources.get('subnets', {})],
        **resources.get('aws:elasticache:ServerlessCache', {}).get('backend', {}),
    )

    backend_cache_primary_endpoint = backend_cache.endpoints.apply(lambda endpoints: endpoints[0]['address'])
    cache_dns = cloudflare.DnsRecord(
        f'{project.name_prefix}-dns-redis',
        name=resources.get('domains', {}).get('redis', None),
        ttl=60,
        type='CNAME',
        zone_id=cloudflare_zone_id,
        content=backend_cache_primary_endpoint,
        proxied=False,
    )

    return (backend_cache, cache_dns)
