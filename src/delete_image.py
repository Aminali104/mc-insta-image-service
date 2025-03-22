import json
import boto3

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')
s3_bucket_name = "mc-image-insta-uploader"
dynamo_table_name = "ImagesMetadata"

def delete_image(event, context):
    try:
        image_id = event['pathParameters']['image_id']

        # Fetch the metadata from DynamoDB to get the S3 key
        response = dynamodb_client.get_item(
            TableName=dynamo_table_name,
            Key={'ImageID': {'S': image_id}}
        )

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }

        s3_key = response['Item']['S3Key']['S']

        # Delete the image from S3
        s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

        # Delete the metadata from DynamoDB
        dynamodb_client.delete_item(
            TableName=dynamo_table_name,
            Key={'ImageID': {'S': image_id}}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image deleted successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
