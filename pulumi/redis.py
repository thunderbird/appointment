import pulumi
import pulumi_cloudflare as cloudflare

from tb_pulumi import ThunderbirdPulumiProject
from tb_pulumi.elasticache import ElastiCacheReplicationGroup
from tb_pulumi.network import MultiCidrVpc, SecurityGroupWithRules


def redis_cache(
    cloudflare_zone_id: str,
    project: ThunderbirdPulumiProject,
    security_groups: list[SecurityGroupWithRules],
    resources: dict,
    vpc: MultiCidrVpc,
):
    """
    Builds a Redis cache.

    :param project: The project to store all the resources in.
    :type project: ThunderbirdPulumiProject

    :param security_groups: List of SecurityGroupWithRules resources which should have access to the new cache replica
        set.
    :type security_groups: list[SecurityGroupWithRules]

    :param resources: The full set of configured resources.
    :type resources: dict

    :param vpc: The VPC to build the cache in.
    :type vpc: MultiCidrVpc

    :return: Tuple with two values:
        - The pulumi_aws.elasticache.ServerlessCache resource
        - The pulumi_cloudflare.DnsRecord resource pointing to the cache
    :rtype: _type_
    """

    redis_replica_group = ElastiCacheReplicationGroup(
        name=f'{project.name_prefix}-redis-replicaset',
        project=project,
        at_rest_encryption_enabled=True,
        cluster_mode='disabled',
        source_sgids=[sg_with_rules.resources['sg'].id for sg_with_rules in security_groups],
        subnets=[subnet for subnet in vpc.resources.get('subnets', {})],
        transit_encryption_enabled=True,
        transit_encryption_mode='preferred',
        **resources.get('tb:elasticache:ElastiCacheReplicationGroup', {}).get('backend', {}),
        opts=pulumi.ResourceOptions(depends_on=[vpc]),
    )
    project.resources['backend_cache_replicaset'] = redis_replica_group

    redis_replica_group_primary_endpoint = redis_replica_group.resources['replication_group'].primary_endpoint_address
    backend_cache_dns = cloudflare.DnsRecord(
        f'{project.name_prefix}-dns-redis',
        name=resources.get('domains', {}).get('redis', None),
        ttl=60,
        type='CNAME',
        zone_id=cloudflare_zone_id,
        content=redis_replica_group_primary_endpoint,
        proxied=False,
    )
    project.resources['backend_cache_dns'] = backend_cache_dns

    return (redis_replica_group, backend_cache_dns)
