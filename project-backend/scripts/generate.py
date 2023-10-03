import os
import sys
import boto3
import argparse

session = boto3.Session(profile_name="CdkDeploy")
cfn = session.client('cloudformation')

branch_name=sys.argv[-1].split('=')[-1]

region = os.environ['CDK_DEPLOY_REGION']
api_url = ''
user_pool_id = ''
user_pool_client_id = ''

outputs = cfn.describe_stacks(StackName=f"BackendInfraStack-{branch_name}")['Stacks'][0]['Outputs']
for output in outputs:
    if output['OutputKey'] == f"ApiEndpoint{branch_name}":
        api_url = output['OutputValue']
    elif output['OutputKey'] == f"UserPoolId{branch_name}":
        user_pool_id = output['OutputValue']
    elif output['OutputKey'] == f"UserPoolWebClient{branch_name}":
        user_pool_client_id = output['OutputValue']

config_string = """
    const awsmobile = {
        aws_cognito_region: "%s",
        aws_user_pools_id: "%s",
        aws_user_pools_web_client_id: "%s",
        aws_cloud_logic_custom: [
            {
                name: "Demo-RestApi-%s",
                endpoint: "%s",
                region: "%s"
            }
        ]
    };
    
    export default awsmobile;
""" % (region, user_pool_id, user_pool_client_id, branch_name, api_url, region)

config_file = open("/home/ubuntu/environment/AmplifyLambdaDemoApp/src/aws-exports.js", 'w')
config_file.write(config_string)
config_file.close()