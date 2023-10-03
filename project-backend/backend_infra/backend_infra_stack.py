from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_cognito as cognito,
    aws_apigateway as apigw
)
from constructs import Construct

class BackendInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, branch_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        user_pool = cognito.UserPool(self, "UserPool", 
            user_pool_name=f"UserPool-{branch_name}",
            self_sign_up_enabled=True,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(email=cognito.StandardAttribute(required=True)),
            removal_policy=RemovalPolicy.DESTROY
        )
        
        client = user_pool.add_client(f"app-client-web-{branch_name}",
            prevent_user_existence_errors=True,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True
            )
        )
        
        authorizer = apigw.CognitoUserPoolsAuthorizer(self, f"API-Authorizer-{branch_name}",
            cognito_user_pools=[user_pool]
        )
        
        lambda_func = _lambda.Function(self, f"Lambda-Func-{branch_name}",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambda/echo-lambda"),
            timeout=Duration.seconds(5)
        )
        
        api = apigw.RestApi(self, "RestApi",
            rest_api_name=f"Demo-RestApi-{branch_name}",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )
        
        echo = api.root.add_resource("echo")
        echo_post_method = echo.add_method("POST", apigw.LambdaIntegration(lambda_func),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        
        CfnOutput(self, f"ApiEndpoint{branch_name}", value=api.url)
        CfnOutput(self, f"UserPoolId{branch_name}", value=user_pool.user_pool_id)
        CfnOutput(self, f"UserPoolWebClient{branch_name}", value=client.user_pool_client_id)