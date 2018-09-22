

def disassociate_iam_instance_profile():
    print(ec2.describe_iam_instance_profile_associations())
    response = ec2.disassociate_iam_instance_profile(
        AssociationId='iip-assoc-0fcd4a354ed1a4a33'
    )

def delete_instance_profile():
    response = iam_client.delete_instance_profile(
        InstanceProfileName='InstanceProfileFor_AmazonEC2ContainerServiceforEC2Role'
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

#print(deregister_task_definition(family_name, '1'))
#print(delete_cluster())
#print(disassociate_iam_instance_profile())
#print(delete_instance_profile())

