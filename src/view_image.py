import json
import boto3
import logging

# Initialize S3 and DynamoDB clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')
s3_bucket_name = "mc-image-insta-uploaders"
dynamo_table_name = "ImagesMetadata"

# Set up logger for debugging and exception tracking
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def view_image(event, context):
    try:
        # Log the incoming event for debugging purposes
        logger.debug("Event received: %s", json.dumps(event))

        # Extract the image_id from path parameters
        image_id = event['pathParameters'].get('image_id')

        if not image_id:
            logger.error("No image_id found in path parameters")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Image ID is required'})
            }

        logger.debug("Fetching metadata for image_id: %s", image_id)

        # Fetch the metadata for the image from DynamoDB
        response = dynamodb_client.get_item(
            TableName=dynamo_table_name,
            Key={'ImageID': {'S': image_id}}
        )

        # Check if the image metadata exists
        if 'Item' not in response:
            logger.warning("Image not found for image_id: %s", image_id)
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }

        # Retrieve the S3 key for the image
        s3_key = response['Item']['S3Key']['S']
        logger.debug("S3 key for image: %s", s3_key)

        # Generate a presigned URL for downloading the image from S3
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # URL valid for 1 hour
        )

        logger.debug("Generated presigned URL: %s", presigned_url)

        # Return the presigned URL in the response
        return {
            'statusCode': 200,
            'body': json.dumps({'url': presigned_url})
        }

    except Exception as e:
        # Log unexpected errors
        logger.error("Error occurred while processing the request: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
