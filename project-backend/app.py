#!/usr/bin/env python3
import os
import aws_cdk as cdk

from account_a_setup.account_a_stack import AccountAStack
from account_b_setup.account_b_setup import AccountBStack
from amplify_app.amplify_app_stack import AmplifyAppStack
from backend_infra.backend_infra_stack import BackendInfraStack

env = cdk.Environment(
    account=os.environ["CDK_DEPLOY_ACCOUNT"] if os.environ["CDK_DEPLOY_ACCOUNT"] != None else os.environ["CDK_DEFAULT_ACCOUNT"], 
    region=os.environ['CDK_DEPLOY_REGION'] if os.environ['CDK_DEPLOY_REGION'] != None else os.environ['CDK_DEFAULT_REGION']
)

app = cdk.App()
branch_name = app.node.try_get_context("branch_name")
AccountAStack(app, "AccountAStack", env=env)
AccountBStack(app, "AccountBStack", env=env)

AmplifyAppStack(app, "AmplifyAppStack", env=env)
BackendInfraStack(app, f"BackendInfraStack-{branch_name}", env=env, branch_name=branch_name)

app.synth()
