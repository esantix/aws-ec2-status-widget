import boto3
import logging

botocore_logger = logging.getLogger('botocore')
botocore_logger.setLevel(logging.WARNING)

def instance_url(instance_id, region):
    """ URL to EC2 instance admin console
    """
    return f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#InstanceDetails:instanceId={instance_id}"


def get_ec2_instances_status(config):
    """ Get all EC2 instaces data in given regions
    """
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
                logging.info(f"Found instance {instance['InstanceId']} in {data['State']} state")

                instances_data.append(data)

    logging.debug(data)
    return instances_data


def stop_instance(config, instance_id, region):
    """ Stop EC2 instance by id
    """
    logging.info(f"Stopping instance {instance_id}...")
    session = boto3.Session(
        profile_name=config["aws_profile"],
        region_name=region,
    )
    ec2 = session.client("ec2")
    ec2.stop_instances(InstanceIds=[instance_id])
    return


def start_instace(config, instance_id, region):
    """ Start EC2 instance by id
    """
    logging.info(f"Starting instance {instance_id}...")
    session = boto3.Session(
        profile_name=config["aws_profile"],
        region_name=region,
    )
    ec2 = session.client("ec2")
    ec2.start_instances(InstanceIds=[instance_id])
    return