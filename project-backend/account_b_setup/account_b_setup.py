import os
import json
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    CfnParameter,
    aws_iam as iam,
    aws_cloud9 as cloud9,
    aws_lambda as _lambda,
    custom_resources as cr
)
from constructs import Construct

class AccountBStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        owner_arn = CfnParameter(self, "Cloud9OwnerArn", type="String",
            description="The Cloud9 Owner ARN. This should be the IAM role for the user who needs access to the machine.")

        cloud9_role = iam.Role(self, "Cloud9Role",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.ServicePrincipal("ssm.amazonaws.com")
            )
        )

        # Restrict permissions based on use case, just make sure this role has access to assume roles
        # for CodeCommit, and CDK
        cloud9_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))

        cloud9_instance_profile=iam.InstanceProfile(self, "Cloud9InstanceProfile",
            instance_profile_name="Cloud9Role",
            role=cloud9_role
        )

        cloud9_env = cloud9.CfnEnvironmentEC2(self, "Cloud9Environment", 
            instance_type="t3.medium",
            automatic_stop_time_minutes=30,
            description="Cloud9 environment",
            image_id="ubuntu-22.04-x86_64",
            name="AccountBEnv",
            owner_arn=owner_arn.value_as_string
        )

        lambda_func = _lambda.Function(self, "Cloud9AssociateInstanceProfileLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambda/cloud9-config"),
            timeout=Duration.seconds(400)
        )
        
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "cloudformation:Describe*",
                "ec2:AssociateIamInstanceProfile",
                "ec2:ModifyInstanceAttribute",
                "ec2:ReplaceIamInstanceProfileAssociation",
                "ec2:DescribeInstances",
                "ec2:DescribeIamInstanceProfileAssociations",
                "iam:ListInstanceProfiles"
            ],
            resources=[
                "*"
            ]
        ))
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "iam:PassRole"
            ],
            resources=[
                cloud9_role.role_arn
            ]
        ))

        cr.AwsCustomResource(self, "AssociateInstanceProfileCR",
            policy=cr.AwsCustomResourcePolicy.from_statements([iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE,
                effect=iam.Effect.ALLOW
            )]),
            timeout=Duration.seconds(400),
            on_create=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                parameters={
                    "FunctionName": lambda_func.function_name,
                    "InvocationType": "Event",
                    "Payload": json.dumps({
                        "EnvironmentId": cloud9_env.ref,
                        "InstanceProfileName": cloud9_instance_profile.instance_profile_name,
                        "InstanceProfileArn": cloud9_instance_profile.instance_profile_arn
                    })
                },
                physical_resource_id=cr.PhysicalResourceId.of("AssociateInstanceProfileCR")
            )
        )
        
        CfnOutput(self, "LambdaRole", value=lambda_func.role.role_arn)
        CfnOutput(self, "InstanceProfileArn", value=cloud9_instance_profile.instance_profile_arn)
        CfnOutput(self, "InstanceProfileName", value=cloud9_instance_profile.instance_profile_name)