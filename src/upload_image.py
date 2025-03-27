import json
import boto3
from uuid import uuid4
from botocore.exceptions import NoCredentialsError
import base64  # Import base64 module for decoding
import logging

# Initialize S3 and DynamoDB clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')
s3_bucket_name = "mc-image-insta-uploaders"
dynamo_table_name = "ImagesMetadata"

# Set up logger for debugging and exception tracking
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def upload_image(event, context):
    try:
        # Log the received event for debugging purposes
        logger.debug("Event received: %s", json.dumps(event))

        # Parse the body of the request
        body = json.loads(event['body'])
        image_data = body.get('image')  # Image data (base64 or direct URL) in the request body
        metadata = body.get('metadata')  # Metadata to be saved in DynamoDB

        if not image_data:
            logger.error("No image data found in request body")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No image data found in the request'})
            }

        if not metadata:
            logger.error("No metadata found in request body")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No metadata found in the request'})
            }

        logger.debug("Decoded image data and metadata received")

        # Decode the base64 image data
        try:
            image_bytes = base64.b64decode(image_data)  # Decode base64 to bytes
            logger.debug("Image data decoded successfully")
        except Exception as decode_error:
            logger.error("Error decoding base64 image data: %s", str(decode_error))
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid base64 image data'})
            }

        # Generate a unique identifier for the image
        image_id = str(uuid4())
        logger.debug("Generated unique image ID: %s", image_id)

        # Upload the image to S3
        s3_key = f"images/{image_id}.jpg"
        try:
            s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=image_bytes, ContentType="image/jpeg")
            logger.debug("Image uploaded to S3 with key: %s", s3_key)
        except Exception as s3_error:
            logger.error("Error uploading image to S3: %s", str(s3_error))
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Error uploading image to S3: {str(s3_error)}'})
            }

        # Store metadata in DynamoDB
        try:
            dynamodb_client.put_item(
                TableName=dynamo_table_name,
                Item={
                    'ImageID': {'S': image_id},
                    'Metadata': {'S': json.dumps(metadata)},
                    'S3Key': {'S': s3_key},
                }
            )
            logger.debug("Metadata stored in DynamoDB for image ID: %s", image_id)
        except Exception as dynamo_error:
            logger.error("Error storing metadata in DynamoDB: %s", str(dynamo_error))
            # Clean up S3 upload if DynamoDB insertion fails
            try:
                s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)
                logger.debug("Image deleted from S3 due to DynamoDB failure: %s", s3_key)
            except Exception as delete_error:
                logger.error("Error deleting image from S3 after DynamoDB failure: %s", str(delete_error))

            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Error storing metadata in DynamoDB: {str(dynamo_error)}'})
            }

        # Return success message
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image uploaded successfully', 'imageId': image_id})
        }

    except NoCredentialsError:
        # Catch AWS credentials errors and log
        logger.error("AWS credentials not found")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'AWS credentials not found'})
        }
    except Exception as e:
        # Log any unhandled exceptions
        logger.error("Unhandled error: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Unhandled error: {str(e)}'})
        }
