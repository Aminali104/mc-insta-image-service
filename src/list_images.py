import json
import boto3

dynamodb_client = boto3.client('dynamodb')
dynamo_table_name = "ImagesMetadata"

def list_images(event, context):
    try:
        # Extract query parameters for filtering
        tag = event['queryStringParameters'].get('tag')
        user_id = event['queryStringParameters'].get('user_id')

        # Query DynamoDB based on filters
        expression = "Metadata LIKE :tag OR Metadata LIKE :user_id"
        expression_values = {
            ":tag": {"S": f"%{tag}%"},
            ":user_id": {"S": f"%{user_id}%"}
        }
        
        response = dynamodb_client.scan(
            TableName=dynamo_table_name,
            FilterExpression=expression,
            ExpressionAttributeValues=expression_values
        )
        
        images = [{"ImageID": item['ImageID']['S'], "Metadata": item['Metadata']['S']} for item in response.get('Items', [])]

        return {
            'statusCode': 200,
            'body': json.dumps({'images': images})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
