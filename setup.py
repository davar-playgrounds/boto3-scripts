import boto3
import json


region_name = 'us-west-2'
ec2 = boto3.client('ec2', region_name=region_name)
ecs = boto3.client('ecs', region_name=region_name)
iam_resource = boto3.resource('iam', region_name=region_name)
iam_client = boto3.client('iam', region_name=region_name)




image = '...'

cluster_name = 'test_cluster3'
family_name = 'family_name1'
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
                'image': image,
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


def run_instances():
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
    )
    instance_id = response['Instances'][0]['InstanceId']
    ec2.create_tags(
        Resources=[instance_id],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'instance name'
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
        RoleName='RoleFor_AmazonEC2ContainerServiceforEC2Role'
    )
    return response


def attach_role_policy():
    response = iam_client.attach_role_policy(
        PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role',
        RoleName='RoleFor_AmazonEC2ContainerServiceforEC2Role'
    )
    return response


def add_role_to_instance_profile():
    instance_profile = iam_resource.create_instance_profile(
        InstanceProfileName='InstanceProfileFor_AmazonEC2ContainerServiceforEC2Role',
    )

    response = iam_client.add_role_to_instance_profile(
        InstanceProfileName='InstanceProfileFor_AmazonEC2ContainerServiceforEC2Role',
        RoleName='RoleFor_AmazonEC2ContainerServiceforEC2Role'
    )
    return response


def associate_iam_instance_profile(instance_id):
    response = ec2.associate_iam_instance_profile(
        IamInstanceProfile={
            'Name': 'InstanceProfileFor_AmazonEC2ContainerServiceforEC2Role'
        },
        InstanceId=instance_id
    )
    return response


def run_task():
    response = ecs.run_task(
        taskDefinition=family_name + ':2',
        cluster=cluster_name
    )
    return response






#print(create_cluster())
#print(register_task_definition())

#response = run_instances()
#instance_id = response['Instances'][0]['InstanceId']
#print(instance_id)

#print(create_role())
#print(attach_role_policy())
#print(add_role_to_instance_profile())

#print(associate_iam_instance_profile(instance_id))


#print(run_task())


