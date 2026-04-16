import json
import pulumi
import pulumi_aws as aws
import tb_pulumi.secrets


def sqs(project, api_exec_role, celery_exec_role):
    # Build a queue
    celery_sqs_queue = aws.sqs.Queue(
        f'{project.name_prefix}-queue-celery',
        fifo_queue=True,
        name=f'{project.name_prefix}-celery.fifo',  # FIFO queue names *must* end in ".fifo"
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
        role=celery_exec_role,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_read_access_policy]),
    )

    aws.iam.RolePolicyAttachment(
        f'{project.name_prefix}-polatt-celerywrite',
        policy_arn=iam_queue_write_access_policy.arn,
        role=celery_exec_role,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_write_access_policy]),
    )

    aws.iam.RolePolicyAttachment(
        f'{project.name_prefix}-polatt-backendwrite',
        policy_arn=iam_queue_write_access_policy.arn,
        role=api_exec_role,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_write_access_policy]),
    )

    # Celery won't let us use container/IMDS permissions; we must supply access key/ID options.
    # Therefore, we must build users with access keys to assign permissions to our running Celery configs.
    read_user = aws.iam.User(
        f'{project.name_prefix}-user',
        name=f'{project.name_prefix}-celery-sqs-read-user',
        path='/',
        tags=project.common_tags,
    )

    read_key_blue = aws.iam.AccessKey(
        f'{project.name_prefix}-celery-sqs-read-key',
        user = read_user,
        status='Active',
    )

    # read_key_green = aws.iam.AccessKey( # Uncomment when we need to rotate credentials
    #     user=read_user,
    #     status='Inactive',
    # )

    write_user = aws.iam.User(
        f'{project.name_prefix}-celery-sqs-write-user',
        name=f'{project.name_prefix}-celery-sqs-write',
        path='/',
        tags=project.common_tags,
    )

    write_key_blue = aws.iam.AccessKey(
        f'{project.name_prefix}-celery-sqs-write-key',
        user = write_user,
        status='Active',
    )

    # write_key_green = aws.iam.AccessKey( # Uncomment when we need to rotate credentials
    #     user=write_user,
    #     status='Inactive',
    # )

    aws.iam.UserPolicyAttachment(
        f'{project.name_prefix}-polatt-celerysqsreader-read',
        policy_arn=iam_queue_read_access_policy,
        user=read_user,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_read_access_policy, read_user])
    )

    aws.iam.UserPolicyAttachment(
        f'{project.name_prefix}-polatt-celerysqswriter-read',
        policy_arn=iam_queue_read_access_policy,
        user=write_user,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_read_access_policy, read_user])
    )

    aws.iam.UserPolicyAttachment(
        f'{project.name_prefix}-polatt-celerysqswriter-write',
        policy_arn=iam_queue_write_access_policy,
        user=write_user,
        opts=pulumi.ResourceOptions(depends_on=[iam_queue_read_access_policy, read_user])
    )

    # Build secrets containing these keys' super secret data
    tb_pulumi.secrets.SecretsManagerSecret(
        f'{project.name_prefix}-secret-celerysqsread-blue',
        project=project,
        secret_name=f'{project.project}/{project.stack}/celerysqsreaduser-blue',
        secret_value={'access_key_id': read_key_blue.id, 'secret_access_key': read_key_blue.secret}
    )

    tb_pulumi.secrets.SecretsManagerSecret(
        f'{project.name_prefix}-secret-celerysqswrite-blue',
        project=project,
        secret_name=f'{project.project}/{project.stack}/celerysqswriteuser-blue',
        secret_value={'access_key_id': read_key_blue.id, 'secret_access_key': read_key_blue.secret}
    )