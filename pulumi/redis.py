import pulumi
import pulumi_aws as aws
import pulumi_cloudflare as cloudflare

from tb_pulumi import ThunderbirdPulumiProject
from tb_pulumi.network import MultiCidrVpc, SecurityGroupWithRules


def redis_cache(
    cloudflare_zone_id: str,
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
    backend_cache = aws.elasticache.ServerlessCache(
        f'{project.name_prefix}-cache-backend',
        security_group_ids=[security_group.resources.get('sg').id],
        subnet_ids=[subnet.id for subnet in vpc.resources.get('subnets', {})],
        tags=project.common_tags,
        **resources.get('aws:elasticache:ServerlessCache', {}).get('backend', {}),
        opts=pulumi.ResourceOptions(depends_on=[vpc]),
    )
    project.resources['backend_cache'] = backend_cache

    backend_cache_primary_endpoint = backend_cache.endpoints.apply(lambda endpoints: endpoints[0]['address'])
    backend_cache_dns = cloudflare.DnsRecord(
        f'{project.name_prefix}-dns-redis',
        name=resources.get('domains', {}).get('redis', None),
        ttl=60,
        type='CNAME',
        zone_id=cloudflare_zone_id,
        content=backend_cache_primary_endpoint,
        proxied=False,
    )
    project.resources['backend_cache_dns'] = backend_cache_dns

    return (backend_cache, backend_cache_dns)
