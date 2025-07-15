import pulumi
import pulumi_aws as aws
import pulumi_cloudflare as cloudflare
import tb_pulumi.cloudfront

from tb_pulumi import ThunderbirdPulumiProject
from tb_pulumi.constants import (
    CLOUDFRONT_CACHE_POLICY_ID_DISABLED,
    CLOUDFRONT_CACHE_POLICY_ID_OPTIMIZED,
    CLOUDFRONT_ORIGIN_REQUEST_POLICY_ID_ALLVIEWER,
)
from tb_pulumi.fargate import FargateClusterWithLogging

#: Where to find the CloudFront function code for our frontend
CLOUDFRONT_REWRITE_CODE_FILE = 'cloudfront-rewrite.js'


def rewrite_function(project: ThunderbirdPulumiProject) -> aws.cloudfront.Function:
    """
    Creates a CloudFront function that rewrites URLs appropriately for this project. The function's code itself is
    manages separately in ``cloudfront-rewrite.js``.

    :param project: Project to store these resources in.
    :type project: ThunderbirdPulumiProject

    :returns: The rewrite function
    :rtype: pulumi_aws.cloudfront.Function
    """

    # Manage the CloudFront rewrite function; the code is managed in cloudfront-rewrite.js
    rewrite_code = None
    try:
        with open(CLOUDFRONT_REWRITE_CODE_FILE, 'r') as fh:
            rewrite_code = fh.read()
    except IOError:
        pulumi.error(f'Could not read file {CLOUDFRONT_REWRITE_CODE_FILE}')

    rewrite_function = aws.cloudfront.Function(
        f'{project.name_prefix}-func-rewrite',
        code=rewrite_code,
        comment='Rewrites inbound requests to direct them to the Appointment backend API',
        name=f'{project.name_prefix}-rewrite',
        publish=True,
        runtime='cloudfront-js-2.0',
    )

    return rewrite_function


def frontend_distribution(
    backend_cluster: FargateClusterWithLogging,
    project: ThunderbirdPulumiProject,
    resources: dict,
    rewrite_function: aws.cloudfront.Function,
) -> aws.cloudfront.Distribution:
    """
    Builds a CloudFront distribution to serve our frontend and rewrite certain requests to the backend.

    :param backend_cluster: The Fargate cluster the backend service runs in.
    :type backend_cluster: FargateClusterWithLogging

    :param project: The project to store these resources in
    :type project: ThunderbirdPulumiProject

    :param resources: The full set of resource configurations
    :type resources: dict

    :param rewrite_function: A CloudFront function that handles rewrites to the backend.
    :type rewrite_function: aws.cloudfront.Function

    :return: The frontend CloudFront distribution.
    :rtype: aws.cloudfront.Distribution
    """

    # Craft the things we need for our CloudFront Distribution, which has a more complex config than this module likes
    backend_domain_name = backend_cluster.resources['fargate_service_alb'].resources['albs']['backend'].dns_name
    backend_origin_id = f'{project.name_prefix}-backend'
    frontend_opts = resources.get('tb:cloudfront:CloudFrontS3Service', {}).get('frontend', {})
    default_cache_behavior = {
        'allowed_methods': ['GET', 'HEAD'],
        'cached_methods': ['GET', 'HEAD'],
        'target_origin_id': f's3-{frontend_opts["service_bucket_name"]}',
        'cache_policy_id': CLOUDFRONT_CACHE_POLICY_ID_OPTIMIZED,
        'function_associations': [{'event_type': 'viewer-request', 'function_arn': rewrite_function.arn}],
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
            'function_associations': [
                {
                    'event_type': 'viewer-request',
                    'function_arn': rewrite_function.arn,
                }
            ],
            'viewer_protocol_policy': 'redirect-to-https',
        },
        {
            'path_pattern': '/fxa',
            'allowed_methods': ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH'],
            'cached_methods': ['GET', 'HEAD', 'OPTIONS'],
            'target_origin_id': backend_origin_id,
            'cache_policy_id': CLOUDFRONT_CACHE_POLICY_ID_DISABLED,
            'origin_request_policy_id': CLOUDFRONT_ORIGIN_REQUEST_POLICY_ID_ALLVIEWER,
            'function_associations': [
                {
                    'event_type': 'viewer-request',
                    'function_arn': rewrite_function.arn,
                }
            ],
            'viewer_protocol_policy': 'redirect-to-https',
        },
    ]
    if 'distribution' in frontend_opts:
        frontend_opts['distribution']['default_cache_behavior'] = default_cache_behavior
        frontend_opts['distribution']['ordered_cache_behaviors'] = ordered_cache_behaviors
    else:
        frontend_opts['distribution'] = {
            'default_cache_behavior': default_cache_behavior,
            'ordered_cache_behaviors': ordered_cache_behaviors,
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
                    'https_port': 443,
                    'origin_protocol_policy': 'https-only',
                    'origin_ssl_protocols': ['TLSv1.2'],
                },
            }
        ],
        **frontend_opts,
        opts=pulumi.ResourceOptions(depends_on=[rewrite_function]),
    )

    return frontend


def posthog_proxy(alias: str, certificate_arn: str, cloudflare_zone_id: str, project: ThunderbirdPulumiProject):
    cache_policy = aws.cloudfront.CachePolicy(
        f'{project.name_prefix}-posthog-cors-policy',
        comment='CORS for Posthog reverse proxy',
        name=f'{project.name_prefix}-posthog-cors',
        parameters_in_cache_key_and_forwarded_to_origin={
            'cookies_config': {'cookie_behavior': 'none'},
            'headers_config': {'header_behavior': 'whitelist', 'headers': {'items': ['Authorization', 'Origin']}},
            'query_strings_config': {'query_string_behavior': 'all'},
        },
    )
    distribution = aws.cloudfront.Distribution(
        f'{project.name_prefix}-posthog-cfdistro',
        aliases=[alias],
        comment=f'Appointment Posthog Proxy ({project.stack})',
        default_cache_behavior={
            'allowed_methods': ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'],
            'cached_methods': ['GET', 'HEAD', 'OPTIONS'],
            'target_origin_id': 'us.i.posthog.com',
            'viewer_protocol_policy': 'allow-all',
            'cache_policy_id': cache_policy.id,
            # Keep these hardcoded until this issue is complete: https://github.com/thunderbird/pulumi/issues/178
            'origin_request_policy_id': '59781a5b-3903-41f3-afcb-af62929ccde1',
            'response_headers_policy_id': 'eaab4381-ed33-4a86-88ca-d9558dc6cd63',
            'compress': True,
            'smooth_streaming': False,
        },
        enabled=True,
        ordered_cache_behaviors=[
            {
                'allowed_methods': ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'],
                'cached_methods': ['GET', 'HEAD', 'OPTIONS'],
                'path_pattern': '/static/*',
                'target_origin_id': 'us-assets.i.posthog.com',
                'viewer_protocol_policy': 'allow-all',
                'cache_policy_id': cache_policy.id,
                'compress': True,
                # Keep these hardcoded until this issue is complete: https://github.com/thunderbird/pulumi/issues/178
                'origin_request_policy_id': '59781a5b-3903-41f3-afcb-af62929ccde1',
                'response_headers_policy_id': 'eaab4381-ed33-4a86-88ca-d9558dc6cd63',
            }
        ],
        origins=[
            {
                'domain_name': 'us-assets.i.posthog.com',
                'origin_id': 'us-assets.i.posthog.com',
                'custom_origin_config': {
                    'http_port': 80,
                    'https_port': 443,
                    'origin_protocol_policy': 'https-only',
                    'origin_ssl_protocols': ['TLSv1.2'],
                },
            },
            {
                'domain_name': 'us.i.posthog.com',
                'origin_id': 'us.i.posthog.com',
                'custom_origin_config': {
                    'http_port': 80,
                    'https_port': 443,
                    'origin_protocol_policy': 'https-only',
                    'origin_ssl_protocols': ['TLSv1.2'],
                },
            },
        ],
        restrictions={'geo_restriction': {'restriction_type': 'none'}},
        viewer_certificate={
            'acm_certificate_arn': certificate_arn,
            'cloudfront_default_certificate': False,
            'minimum_protocol_version': 'TLSv1.2_2021',
            'ssl_support_method': 'sni-only',
        },
        opts=pulumi.ResourceOptions(delete_before_replace=True),
    )
    dns_record = cloudflare.DnsRecord(
        f'{project.name_prefix}-posthog-dns',
        content=distribution.domain_name,
        name='data.appointment.tb.pro',
        proxied=False,
        ttl=60,
        type='CNAME',
        zone_id=cloudflare_zone_id,
    )

    return (cache_policy, distribution, dns_record)
