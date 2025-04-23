import boto3
import logging

logging.basicConfig(level=logging.INFO)


def get_ec2_instances_status(config):

    instances = []

    for region in config["regions"]:
        session = boto3.Session(
            profile_name=config["aws_profile"],
            region_name=region,
        )
        ec2 = session.client("ec2")
        response = ec2.describe_instances()

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                data = instance

                instance_id = instance["InstanceId"]
                status = instance["State"]["Name"]
                instance_type = instance["InstanceType"]

                instances.append((instance_id, status, instance_type, region, data))

    return instances


def stop_instance(_, config, instance, region):
    session = boto3.Session(
        profile_name=config["aws_profile"],
        region_name=region,
    )
    ec2 = session.client("ec2")
    ec2.stop_instances(InstanceIds=[instance])
    return


def start_instace(_, config, instance, region):
    print("Starting...")
    session = boto3.Session(
        profile_name=config["aws_profile"],
        region_name=region,
    )
    ec2 = session.client("ec2")
    ec2.start_instances(InstanceIds=[instance])
    return