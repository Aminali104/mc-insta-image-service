import json
import boto3
from uuid import uuid4
from botocore.exceptions import NoCredentialsError

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')
s3_bucket_name = "mc-image-insta-uploader"
dynamo_table_name = "ImagesMetadata"

def upload_image(event, context):
    try:
        body = json.loads(event['body'])
        image_data = body['image']  # Image data (base64 or direct URL) in the request body
        metadata = body['metadata']  # Metadata to be saved in DynamoDB

        # Generate a unique identifier for the image
        image_id = str(uuid4())

        # Upload the image to S3
        s3_key = f"images/{image_id}.jpg"
        s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=image_data)

        # Store metadata in DynamoDB
        dynamodb_client.put_item(
            TableName=dynamo_table_name,
            Item={
                'ImageID': {'S': image_id},
                'Metadata': {'S': json.dumps(metadata)},
                'S3Key': {'S': s3_key},
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image uploaded successfully', 'imageId': image_id})
        }

    except NoCredentialsError:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'AWS credentials not found'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
