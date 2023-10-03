import json

def lambda_handler(event, context):
    print(event)
    body = json.loads(event['body'])
    print(body)
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Expose-Headers": "*"
        },
        'body': json.dumps({"Message": f"Test 2: {body['Message']}"})
    }