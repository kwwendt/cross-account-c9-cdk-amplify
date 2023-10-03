from __future__ import print_function
import boto3
import json
import os
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    logger.info("event: {}".format(event))
    logger.info("context: {}".format(context))
    responseData = {}

    try:
        # Get the InstanceId of the Cloud9 IDE
        instance = ec2.describe_instances(
            Filters=[
                {
                    "Name": "tag:aws:cloud9:environment",
                    "Values": [event["EnvironmentId"]],
                }
            ]
        )["Reservations"][0]["Instances"][0]
        logger.info("instance: {}".format(instance))

        # Create the IamInstanceProfile request object
        iam_instance_profile = {
            "Arn": event["InstanceProfileArn"],
            "Name": event["InstanceProfileName"],
        }
        logger.info("iam_instance_profile: {}".format(iam_instance_profile))

        # Wait for Instance to become ready before adding Role
        instance_state = instance["State"]["Name"]
        logger.info("instance_state: {}".format(instance_state))
        while instance_state != "running":
            time.sleep(5)
            instance_state = ec2.describe_instances(
                InstanceIds=[instance["InstanceId"]]
            )
            logger.info("instance_state: {}".format(instance_state))

        # attach instance profile
        response = ec2.associate_iam_instance_profile(
            IamInstanceProfile=iam_instance_profile,
            InstanceId=instance["InstanceId"],
        )
        logger.info(
            "response - associate_iam_instance_profile: {}".format(response)
        )

        responseData = {
            "Success": "Started bootstrapping for instance: "
            + instance["InstanceId"]
        }
        return responseData

    except Exception as e:
        logger.error(e, exc_info=True)
        responseData = {
            "Error": "There was a problem associating IAM profile to the Cloud9 Instance"
        }
        return responseData
