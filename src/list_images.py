import json
import boto3
import logging

# Initialize DynamoDB client
dynamodb_client = boto3.client('dynamodb')
dynamo_table_name = "ImagesMetadata"

# Set up logger for debugging and exception tracking
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def list_images(event, context):
    try:
        # Log the event received for debugging purposes
        logger.debug("Event received: %s", json.dumps(event))
        
        # Extract query parameters from the event
        query_params = event.get('queryStringParameters', {})
        logger.debug("Query parameters: %s", query_params)

        # If query parameters are None or empty, scan the entire table
        if not query_params:
            logger.debug("No filters provided, returning all images")
            try:
                # Perform DynamoDB scan without any filter expression
                response = dynamodb_client.scan(
                    TableName=dynamo_table_name
                )
                logger.debug("DynamoDB scan successful, retrieved %d items", len(response.get('Items', [])))
            except Exception as scan_error:
                logger.error("Error performing scan on DynamoDB: %s", str(scan_error))
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f'Error performing scan on DynamoDB: {str(scan_error)}'})
                }

        else:
            # If filters are provided, build the filter expression
            logger.debug("Filters found, building filter expression")

            tag = query_params.get('tag')
            user_id = query_params.get('user_id')

            # Initialize filter expression and expression attribute values
            filter_expression = []
            expression_values = {}

            # Add filter for 'tag' if it's provided
            if tag:
                filter_expression.append("contains(Metadata, :tag)")
                expression_values[":tag"] = {"S": tag}
                logger.debug("Filter for tag: %s", tag)

            # Add filter for 'user_id' if it's provided
            if user_id:
                filter_expression.append("contains(Metadata, :user_id)")
                expression_values[":user_id"] = {"S": user_id}
                logger.debug("Filter for user_id: %s", user_id)

            # If no filters were added, scan the entire table
            if not filter_expression:
                logger.debug("No valid filters provided, returning all images")
                try:
                    # Perform DynamoDB scan without filters
                    response = dynamodb_client.scan(
                        TableName=dynamo_table_name
                    )
                    logger.debug("DynamoDB scan successful, retrieved %d items", len(response.get('Items', [])))
                except Exception as scan_error:
                    logger.error("Error performing scan on DynamoDB: %s", str(scan_error))
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': f'Error performing scan on DynamoDB: {str(scan_error)}'})
                    }
            else:
                # If filters are present, join them into a single string
                filter_expression_str = " AND ".join(filter_expression)
                logger.debug("Filter expression: %s", filter_expression_str)

                try:
                    # Perform DynamoDB scan with filter expression
                    response = dynamodb_client.scan(
                        TableName=dynamo_table_name,
                        FilterExpression=filter_expression_str,
                        ExpressionAttributeValues=expression_values
                    )
                    logger.debug("DynamoDB scan successful with filter, retrieved %d items", len(response.get('Items', [])))
                except Exception as scan_error:
                    logger.error("Error performing scan with filter expression: %s", str(scan_error))
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': f'Error performing scan with filter expression: {str(scan_error)}'})
                    }

        # Process the response from DynamoDB and format the images
        images = [{"ImageID": item['ImageID']['S'], "Metadata": item['Metadata']['S']} for item in response.get('Items', [])]
        logger.debug("Processed %d images", len(images))

        return {
            'statusCode': 200,
            'body': json.dumps({'images': images})
        }

    except Exception as e:
        # Log the error and return an internal server error response
        logger.error("Unhandled error: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Unhandled error: {str(e)}'})
        }
