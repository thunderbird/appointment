import json
import pulumi
import pulumi_aws as aws

def sqs(project, api_exec_role, celery_exec_role):
    # Build a queue
    pulumi.info(f'{project.name_prefix}-celery')
    celery_sqs_queue = aws.sqs.Queue(
        f'{project.name_prefix}-queue-celery',
        fifo_queue=True,
        name=f'{project.name_prefix}-celery.fifo',
        # policy=json.dumps(
        #     {
        #         'Version': '2012-10-17',
        #         'Id': 'OwnerAccessPolicy',
        #         'Statement': [
        #             {
        #                 'Sid': 'OwnerAccessStatement',
        #                 'Effect': 'Allow',
        #                 'Principal': {'AWS': '768512802988'},
        #                 'Action': ['SQS:*'],
        #                 'Resource': 'arn:aws:sqs:eu-central-1:768512802988:rjung-test',
        #             }
        #         ],
        #     }
        # ),
        tags=project.common_tags,
    )

    # Build IAM policies allowing receipt and publication of messages to the queue
    iam_read_policy_doc = celery_sqs_queue.arn.apply(
        lambda queue_arn: json.dumps(
            {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Sid': 'AllowSQSReceipt',
                        'Effect': 'Allow',
                        'Action': [
                            'sqs:ChangeMessageVisibility',
                            'sqs:DeleteMessage',
                            'sqs:ReceiveMessage',
                        ],
                        'Resource': [
                            queue_arn,
                        ],
                    }
                ],
            }
        )
    )

    iam_queue_read_access_policy = aws.iam.Policy(
        f'{project.name_prefix}-iampolicy-celerysqs-read',
        description=f'Allow subscription to the {project.name_prefix}-celery SQS queue',
        name=f'{project.name_prefix}-celery-read',
        policy=iam_read_policy_doc,
        tags=project.common_tags,
        opts=pulumi.ResourceOptions(depends_on=[celery_sqs_queue]),
    )

    iam_write_policy_doc = celery_sqs_queue.arn.apply(
        lambda queue_arn: json.dumps(
            {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Sid': 'AllowSQSPublication',
                        'Effect': 'Allow',
                        'Action': [
                            'sqs:SendMessage',
                        ],
                        'Resource': [queue_arn],
                    }
                ],
            }
        )
    )

    iam_queue_write_access_policy = aws.iam.Policy(
        f'{project.name_prefix}-iampolicy-celerysqs-write',
        description=f'Allow publication to the {project.name_prefix}-celery SQS queue',
        name=f'{project.name_prefix}-celery-write',
        policy=iam_write_policy_doc,
        tags=project.common_tags,
        opts=pulumi.ResourceOptions(depends_on=[celery_sqs_queue]),
    )

    # Attach those policies to the appropriate containers
    aws.iam.RolePolicyAttachment(
        f'{project.name_prefix}-polatt-celeryread',
        policy_arn=iam_queue_read_access_policy.arn,
        role=api_exec_role,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_read_access_policy]),
    )
    aws.iam.RolePolicyAttachment(
        f'{project.name_prefix}-polatt-celerywrite',
        policy_arn=iam_queue_write_access_policy.arn,
        role=api_exec_role,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_write_access_policy]),
    )
    aws.iam.RolePolicyAttachment(
        f'{project.name_prefix}-polatt-backendwrite',
        policy_arn=iam_queue_write_access_policy.arn,
        role=api_exec_role,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_write_access_policy]),
    )
