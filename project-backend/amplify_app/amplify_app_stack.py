from aws_cdk import (
    Stack,
    CfnOutput,
    CfnParameter,
    custom_resources as cr,
    aws_iam as iam,
    aws_codecommit as codecommit
)
from aws_cdk.aws_amplify_alpha import (
    App, 
    Branch,
    CustomRule,
    AutoBranchCreation,
    CodeCommitSourceCodeProvider,
    RedirectStatus
)
from constructs import Construct

class AmplifyAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        repo_name = CfnParameter(self, "RepoName", type="String", default="AmplifyLambdaDemoApp",
            description="The name of the CodeCommit repo where the source code will be hosted.")
        
        repo = codecommit.Repository.from_repository_name(self, "FrontendRepo", repo_name.value_as_string)
        
        service_role = iam.Role(self, "AmplifyServiceRole", 
            assumed_by=iam.ServicePrincipal("amplify.amazonaws.com")
        )
        repo.grant_pull(service_role)
        service_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"  
            ],
            resources=[
                "*"   
            ]
        ))
        
        app = App(self, "DemoApp", 
            app_name="DemoApp",
            role=service_role,
            source_code_provider=CodeCommitSourceCodeProvider(
                repository=repo
            ),
            auto_branch_creation=AutoBranchCreation(
                patterns=["feature/*", "test/*"]),
            auto_branch_deletion=True
        )
        app.add_custom_rule(rule=CustomRule(
            source="</^[^.]+$|\\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json|webp)$)([^.]+$)/>",
            target='/index.html',
            status=RedirectStatus.REWRITE
        ))
        
        env = app.add_branch("main")
        
        cr.AwsCustomResource(self, "StartAmplifyBuild", 
            on_create=cr.AwsSdkCall(
                service="Amplify",
                action="startJob",
                physical_resource_id=cr.PhysicalResourceId.of('amplify-build-trigger'),
                parameters={
                  "appId": app.app_id,
                  "branchName": env.branch_name,
                  "jobType": 'RELEASE',
                  "jobReason": 'Initial build deployment after stack creation.'
                }
            ),
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            )
        )
        
        CfnOutput(self, "AmplifyAppId", value=app.app_id)
        CfnOutput(self, "AmplifyAppUrl", value=f"main.{app.default_domain}")