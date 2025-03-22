import json
import boto3

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')
s3_bucket_name = "mc-image-insta-uploader"
dynamo_table_name = "ImagesMetadata"

def view_image(event, context):
    try:
        image_id = event['pathParameters']['image_id']
        
        # Fetch the metadata from DynamoDB
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

        # Generate a presigned URL for downloading the image
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket_name, 'Key': s3_key},
            ExpiresIn=3600
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'url': presigned_url})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
