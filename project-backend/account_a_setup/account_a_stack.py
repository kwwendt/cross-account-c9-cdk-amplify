import os
from aws_cdk import (
    Stack,
    CfnParameter,
    aws_iam as iam,
    aws_codecommit as codecommit
)
from constructs import Construct

class AccountAStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account_b_id = CfnParameter(self, "AccountBId", type="String",
            description="The AWS Account ID for account B")
        
        repo = codecommit.Repository(self, "AmplifyLambdaDemoAppRepo", 
            repository_name="AmplifyLambdaDemoApp"
        )

        cross_account_role = iam.Role(self, "CrossAccountContributorRole",
            role_name="CrossAccountContributorRole",
            assumed_by=iam.AccountPrincipal(account_b_id.value)
        )
        cross_account_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "codecommit:BatchGet*",
                "codecommit:Create*",
                "codecommit:DeleteBranch",
                "codecommit:Get*",
                "codecommit:List*",
                "codecommit:Describe*",
                "codecommit:Put*",
                "codecommit:Post*",
                "codecommit:Merge*",
                "codecommit:Test*",
                "codecommit:Update*",
                "codecommit:GitPull",
                "codecommit:GitPush"
            ],
            resources=[
                repo.repository_arn
            ]
        ))