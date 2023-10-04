# Cross account AWS Cloud9, AWS CDK, and AWS Amplify

This repository provides steps to set up cross-account roles and projects for Cloud9, CDK, and Amplify development.

![Architecture diagram](/img/C9-Cross-Account.png)

## Pre-requisites

1. You must have 2 AWS accounts to walk through this tutorial with administrative privileges to configure AWS IAM roles and resources.

## Account A set up steps

Account A is where the resources will be deployed into.

1. Open a CloudShell terminal and clone this repository - [documentation](https://docs.aws.amazon.com/cloudshell/latest/userguide/getting-started.html).

```
git clone https://github.com/kwwendt/cross-account-c9-cdk-amplify.git
```

2. Upgrade CDK version and install required libraries by running the following commands:

```
sudo npm install -g aws-cdk@latest
cd cross-account-c9-cdk-amplify/project-backend
pip3 install -r requirements.txt
```

3. Bootstrap the CDK account using the following command, replacing `<account A ID>`, `<account B ID>`, and `<region>` with the correct values.

```
export CDK_DEPLOY_ACCOUNT=<account A ID>
export CDK_DEPLOY_REGION=<region>
cdk bootstrap --trust <account B ID> --trust-for-lookup <account B ID> --cloudformation-execution-policies "arn:aws:iam::aws:policy/AdministratorAccess"
```

The bootstrap process should success with a message similar to:
```
CDKToolkit: creating CloudFormation changeset...
 ✅  Environment aws://<account A ID>/<region> bootstrapped.
```

4. Deploy AWS CodeCommit resources and IAM role by running the following command, replacing `<account B ID>` with the correct value. Confirm the deployment by typing `y` when prompted.

```
cdk deploy AccountAStack --parameters AccountBId=<account B ID>
```

## Account B set up steps

Account B will have the AWS Cloud9 development environments. The below steps will deploy 

1. Open a CloudShell terminal and clone this repository - [documentation](https://docs.aws.amazon.com/cloudshell/latest/userguide/getting-started.html).

```
git clone https://github.com/kwwendt/cross-account-c9-cdk-amplify.git
```

2. Upgrade CDK version and install required libraries by running the following commands:

```
sudo npm install -g aws-cdk@latest
cd cross-account-c9-cdk-amplify/project-backend
pip3 install -r requirements.txt
```

3. Bootstrap the CDK account using the following command, replacing `<account B ID>` and `<region>` with the correct values.

```
export CDK_DEPLOY_ACCOUNT=<account A ID>
export CDK_DEPLOY_REGION=<region>
cdk bootstrap
```

The bootstrap process should success with a message similar to:

```
CDKToolkit: creating CloudFormation changeset...
 ✅  Environment aws://<account A ID>/<region> bootstrapped.
```

 4. Deploy AWS Cloud9 resources by running the following command. Enter in the Owner ARN who should be able to access this machine. Confirm the deployment by typing `y` when prompted. Ex: arn:aws:iam::<account B ID>:assumed-role/admin/testuser

```
cdk deploy AccountBStack --parameters Cloud9OwnerArn=arn:aws:sts::<account B ID>:assumed-role/<federated user>
```

## Run the deployments

In Account B, open the Cloud9 environment.

1. Turn off managed temporary credentials for the Cloud9 environment so the credentials use the IAM instance profile.
- Click settings, scroll down to AWS Settings --> turn off Managed temporary credentials

2. Configure the AWS config for different AWS profiles.

```
touch ~/.aws/config
```

3. Add the following into the newly created `~/.aws/config` file using VI. Replace the account A ID and region with appropriate values.

```
[default]
region = <region>
output = json

[profile CrossAccount]
role_arn = arn:aws:iam::<account A ID>:role/CrossAccountContributorRole
credential_source = Ec2InstanceMetadata
role_session_name = testuser
region = <region>
output = json
```

4. Clone the repository (first from GitHub) then update the origin to AWS CodeCommit. Push code changes to repo.

```
git clone https://github.com/kwwendt/cross-account-c9-cdk-amplify.git
cd ~/environment/cross-account-c9-cdk-amplify
rm -rf .git
cd ~/environment/cross-account-c9-cdk-amplify/AmplifyLambdaDemoApp
git init -b main
git remote add origin codecommit://CrossAccount@AmplifyLambdaDemoApp
git add .
git commit -m "Push initial changes."
git push origin main
```

5. Prepare scripts and install packages.

```
cd ~/environment/cross-account-c9-cdk-amplify/project-backend
pip3 install -r requirements.txt
chmod +x scripts/cdk-deploy-to.sh
chmod +x scripts/cdk-destroy.sh
```

6. Deploy backend infrastructure. Replace the account and region with the appropriate values. Confirm the deployment when prompted.

```
cd ~/environment/cross-account-c9-cdk-amplify/project-backend
./scripts/cdk-deploy-to.sh <account A ID> <region> BackendInfraStack-main -c branch_name=main
```

7. Commit changes to repo and deploy Amplify stack.

```
cd ~/environment/cross-account-c9-cdk-amplify/AmplifyLambdaDemoApp
npm install
git add .
git commit -m "Updated main branch code"
git push origin main

./scripts/cdk-deploy-to.sh <account A ID> <region> AmplifyAppStack --parameters RepoName=AmplifyLambdaDemoApp
```