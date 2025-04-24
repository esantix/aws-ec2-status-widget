import boto3
import logging

logging.basicConfig(level=logging.INFO)


def instance_link(instance_id, region):
    return f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#InstanceDetails:instanceId={instance_id}"


def get_ec2_instances_status(config):

    instances_data = []

    for region in config["regions"]:
        logging.info(f"Fetching {region} data")
        session = boto3.Session(
            profile_name=config["aws_profile"],
            region_name=region,
        )
        ec2 = session.client("ec2")
        response = ec2.describe_instances()

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                data = instance
                data["Region"] = region
                data["State"] = instance["State"]["Name"]
                logging.info(f"Found instance {instance['InstanceId']}")

                instances_data.append(data)

    logging.debug(data)
    return instances_data


def stop_instance(_, config, instance_id, region):
    session = boto3.Session(
        profile_name=config["aws_profile"],
        region_name=region,
    )
    ec2 = session.client("ec2")
    ec2.stop_instances(InstanceIds=[instance_id])
    return


def start_instace(_, config, instance_id, region):
    print("Starting...")
    session = boto3.Session(
        profile_name=config["aws_profile"],
        region_name=region,
    )
    ec2 = session.client("ec2")
    ec2.start_instances(InstanceIds=[instance_id])
    return