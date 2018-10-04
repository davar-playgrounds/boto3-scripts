import boto3
import config
import time

region_name = config.region_name
ec2 = boto3.client('ec2', region_name=region_name)
ecs = boto3.client('ecs', region_name=region_name)
iam_resource = boto3.resource('iam', region_name=region_name)
iam_client = boto3.client('iam', region_name=region_name)

image = config.image
cluster_name = config.cluster_name
family_name = config.family_name
family_version = config.family_version


def disassociate_iam_instance_profile():
    print(ec2.describe_iam_instance_profile_associations())


def delete_instance_profile():
    response = iam_client.delete_instance_profile(
        InstanceProfileName=config.ec2_instance_profile
    )
    return response


def deregister_task_definition(task_definition, version):
    response = ecs.deregister_task_definition(
        taskDefinition=task_definition + ':' + version
    )
    return response


def delete_cluster():
    response = ecs.delete_cluster(
        cluster=cluster_name
    )
    return response


def remove_role_from_instance_profile():
    iam_client.remove_role_from_instance_profile(
        InstanceProfileName=config.ec2_instance_profile,
        RoleName=config.ec2_container_service_role
    )

def delete_security_group():
    ec2.delete_security_group(
        GroupName=config.security_group_name
    )


def detach_policy():
    role = iam_resource.Role(config.ec2_container_service_role)
    role.detach_policy(PolicyArn=config.aws_ec2_container_service_role)


def delete_role():
    role = iam_resource.Role(config.ec2_container_service_role)
    role.delete()


def teardown():
    print(delete_cluster())
    print(deregister_task_definition(family_name, family_version))
    delete_security_group()
    detach_policy()
    remove_role_from_instance_profile()
    time.sleep(3)
    delete_role()
    print(disassociate_iam_instance_profile())
    print(delete_instance_profile())


if __name__ == "__main__":
    teardown()
