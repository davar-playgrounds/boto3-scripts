import boto3
import json
import config

region_name = config.region_name
ec2 = boto3.client('ec2', region_name=region_name)
ecs = boto3.client('ecs', region_name=region_name)
iam_resource = boto3.resource('iam', region_name=region_name)
iam_client = boto3.client('iam', region_name=region_name)

image = config.image
cluster_name = config.cluster_name
family_name = config.family_name
family_version = config.family_version
instance_name = config.instance_name

user_data_script = """#!/bin/bash
echo ECS_CLUSTER=""" + cluster_name + " >> /etc/ecs/ecs.config"


def create_cluster():
    response = ecs.create_cluster(
        clusterName=cluster_name
    )
    return response


def register_task_definition():
    result = ecs.register_task_definition(
        family=family_name,
        containerDefinitions=[
            {
                'name': 'container_name1',
                #'image': image,
                'image': '...',
                'cpu': 123,
                'memory': 123,
                'memoryReservation': 123,
                'portMappings': [
                    {
                        'containerPort': 8000,
                        'hostPort': 80,
                    },
                ],
                'environment': [
                    {
                        'name': 'TEST_ENV_VAR',
                        'value': 'TEST_ENV_VAR value'
                    },
                ]
            },
        ]
    )
    return result


def run_instances(security_group_id):
    response = ec2.run_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                     'DeleteOnTermination': True,
                     'VolumeSize': 8,
                     'VolumeType': 'gp2'
                },
            },
        ],
        ImageId='ami-00430184c7bb49914',
        InstanceType='m3.medium',
        MaxCount=1,
        MinCount=1,
        UserData=user_data_script,
        SecurityGroupIds=security_group_id
    )
    instance_id = response['Instances'][0]['InstanceId']
    ec2.create_tags(
        Resources=[instance_id],
        Tags=[
            {
                'Key': 'Name',
                'Value': config.instance_name
            },
        ]
    )
    return response


def create_role():
    trust_policy = {
        'Version': '2012-10-17',
        'Statement': {
            'Effect': 'Allow',
            'Principal': {
                'Service': 'ec2.amazonaws.com'
            },
            'Action': 'sts:AssumeRole'
        }
    }

    response = iam_client.create_role(
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        RoleName=config.ec2_container_service_role
    )

    iam_client.attach_role_policy(
        PolicyArn=config.aws_ec2_container_service_role,
        RoleName=config.ec2_container_service_role
    )
    return response


def create_instance_profile():
    instance_profile = iam_resource.create_instance_profile(
        InstanceProfileName=config.ec2_instance_profile,
    )
    return instance_profile


def add_role_to_instance_profile():
    response = iam_client.add_role_to_instance_profile(
        InstanceProfileName=config.ec2_instance_profile,
        RoleName=config.ec2_container_service_role
    )
    return response


def associate_iam_instance_profile(instance_id):
    response = ec2.associate_iam_instance_profile(
        IamInstanceProfile={
            'Name': config.ec2_instance_profile
        },
        InstanceId=instance_id
    )
    return response


def run_task():
    response = ecs.run_task(
        taskDefinition=family_name + family_version,
        cluster=cluster_name
    )
    return response


def create_security_group():
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    response = ec2.create_security_group(
        GroupName=config.security_group_name,
        VpcId=vpc_id,
        Description='Security grooup for EC2 instances')

    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[{
                'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{
                     'CidrIp': '0.0.0.0/0'
                 }]
            },
            {
                'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{
                     'CidrIp': '0.0.0.0/0'
                 }]
            }
        ])
    print('Ingress Successfully Set %s' % data)
    return security_group_id


def setup():
    print('create_cluster', create_cluster())
    print('register_task_definition', register_task_definition())
    security_group_id = create_security_group()
    print('security_group_id', security_group_id)
    print('create_role', create_role())
    print('create_instance_profile', create_instance_profile())
    print(add_role_to_instance_profile())

    response = run_instances([security_group_id])
    instance_id = response['Instances'][0]['InstanceId']

    waiter = ec2.get_waiter('instance_running')
    waiter.wait(
        InstanceIds=[
            instance_id,
        ]
    )

    print('instance_id: ', instance_id)
    print(associate_iam_instance_profile(instance_id))
    print(run_task())
    pass


if __name__ == "__main__":
    setup()
