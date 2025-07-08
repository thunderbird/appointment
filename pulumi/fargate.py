import pulumi
import tb_pulumi.fargate

from tb_pulumi import ThunderbirdPulumiProject
from tb_pulumi.network import MultiCidrVpc

#: Error message for mismatched LB/cluster names
MSG_LB_MATCHING_CLUSTER = 'In this stack, Fargate clusters must have matching load balancer security groups.'
#: Error message for mismatched cluster/security group names
MSG_CONTAINER_MATCHING_CLUSTER = 'In this stack, Fargate clusters must have matching container security groups.'


def fargate(
    container_security_groups: dict,
    load_balancer_security_groups: dict,
    project: ThunderbirdPulumiProject,
    resources: dict,
    vpc: MultiCidrVpc,
) -> dict:
    """
    Builds out all Fargate clusters defined in the resource config.

    :param container_security_groups: Dict of security groups for the containers.
    :type container_security_groups: dict

    :param load_balancer_security_groups: Dict of security groups for the load balancers.
    :type load_balancer_security_groups: dict

    :param project: Project to store these resources in.
    :type project: ThunderbirdPulumiProject

    :param resources: Full set of resource config options.
    :type resources: dict

    :param vpc: The VPC to install the clusters in.
    :type vpc: MultiCidrVpc

    :raises ValueError: When there is no load balancer security group matching the name of the service.
    :raises ValueError: When there is no container security group matching the name of the service.

    :returns: A dict of fargate clusters
    :rtype: dict
    """

    fargate_clusters = {}
    for service, opts in resources['tb:fargate:FargateClusterWithLogging'].items():
        if service not in load_balancer_security_groups:
            raise ValueError(f'{MSG_LB_MATCHING_CLUSTER} Create a matching load_balancers entry for "{service}".')
        if service not in container_security_groups:
            raise ValueError(
                f'{MSG_CONTAINER_MATCHING_CLUSTER} Create a matching containers entry for "{service}".'
            )
        lb_sg_ids = (
            [load_balancer_security_groups[service].resources['sg'].id]
            if load_balancer_security_groups[service]
            else []
        )
        depends_on = [
            container_security_groups[service].resources['sg'],
            *vpc.resources['subnets'],
        ]
        if load_balancer_security_groups[service]:
            depends_on.append(load_balancer_security_groups[service].resources['sg'])
        fargate_clusters[service] = tb_pulumi.fargate.FargateClusterWithLogging(
            name=f'{project.name_prefix}-fargate-{service}',
            project=project,
            subnets=vpc.resources['subnets'],
            container_security_groups=[container_security_groups[service].resources['sg'].id],
            load_balancer_security_groups=lb_sg_ids,
            opts=pulumi.ResourceOptions(depends_on=depends_on),
            **opts,
        )

    return fargate_clusters
