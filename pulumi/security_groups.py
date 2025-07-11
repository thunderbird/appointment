import tb_pulumi.network
import pulumi

from tb_pulumi import ThunderbirdPulumiProject

#: Error message for mismatched LB/container names
MSG_LB_MATCHING_CONTAINER = 'In this stack, container security groups must have matching load balancer security groups.'


def security_groups(
    project: ThunderbirdPulumiProject,
    resources: dict,
    vpc: tb_pulumi.network.MultiCidrVpc,
) -> tuple:
    """
    Builds the defined security groups to be used for load balancers and Fargate containers.

    :param project: The project these resources belong to.
    :type project: tb_pulumi.ThunderbirdPulumiProject

    :param resources: The config dict representing all resource configurations.
    :type resources: dict

    :param vpc: The MultiCidrVpc these security groups should be built in.
    :type vpc: tb_pulumi.network.MultiCidrVpc

    :returns: Tuple containing these three values:
        - Backend Redis cache security group
        - Dict of security groups for containers
        - Dict of security groups for load balancers
    :rtype: tuple
    """

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

    # Build a security group to allow traffic from containers into Redis
    backend_cache_sg_opts = (
        resources.get('tb:network:SecurityGroupWithRules', {}).get('other', {}).get('backend_cache', {})
    )
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

    return (backend_cache_sg, container_sgs, lb_sgs)
