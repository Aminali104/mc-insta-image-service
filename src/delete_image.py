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

def delete_image(event, context):
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

        # Fetch the metadata from DynamoDB to get the S3 key
        response = dynamodb_client.get_item(
            TableName=dynamo_table_name,
            Key={'ImageID': {'S': image_id}}
        )

        # Check if the image exists in DynamoDB
        if 'Item' not in response:
            logger.warning("Image not found for image_id: %s", image_id)
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }

        # Retrieve the S3 key of the image
        s3_key = response['Item']['S3Key']['S']
        logger.debug("S3 key for image: %s", s3_key)

        # Delete the image from S3
        logger.debug("Deleting image from S3 with key: %s", s3_key)
        s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

        # Delete the metadata from DynamoDB
        logger.debug("Deleting metadata for image_id: %s from DynamoDB", image_id)
        dynamodb_client.delete_item(
            TableName=dynamo_table_name,
            Key={'ImageID': {'S': image_id}}
        )

        # Return success message
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image deleted successfully'})
        }

    except Exception as e:
        # Log the error
        logger.error("Error occurred while deleting the image: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
