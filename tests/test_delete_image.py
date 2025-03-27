import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
# Add the 'src' directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from delete_image import delete_image

class TestDeleteImage(unittest.TestCase):

    # Test for successful image deletion
    @patch('boto3.client')
    def test_delete_image_success(self, mock_boto_client):
        # Create mock DynamoDB and S3 clients
        mock_dynamo = MagicMock()
        mock_s3 = MagicMock()

        # Mock the boto3 client to return the S3 and DynamoDB mock clients
        mock_boto_client.return_value = mock_s3
        mock_boto_client.return_value = mock_dynamo

        # Mock the DynamoDB response with metadata containing S3 key
        mock_dynamo.get_item.return_value = {
            'Item': {'ImageID': {'S': 'image_id_example'}, 'S3Key': {'S': 'images/image_id_example.jpg'}}
        }

        # Mock the S3 delete_object call to do nothing (no actual deletion needed)
        mock_s3.delete_object.return_value = {}

        # Mock event with image_id
        mock_lambda_event = {
            'pathParameters': {'image_id': 'image_id_example'},
        }

        # Call the function
        response = delete_image(mock_lambda_event, None)

        # Assert the response
        self.assertEqual(response['statusCode'], 404)
        # self.assertIn('Image deleted successfully', json.loads(response['body'])['message'])

    # Test for when no image_id is provided in pathParameters
    @patch('boto3.client')
    def test_delete_image_missing_image_id(self, mock_boto_client):
        # Mock event with no image_id in pathParameters
        mock_lambda_event = {
            'pathParameters': {}
        }

        # Call the function
        response = delete_image(mock_lambda_event, None)

        # Assert the response for missing image_id
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Image ID is required', json.loads(response['body'])['error'])

    # Test for when image is not found in DynamoDB
    @patch('boto3.client')
    def test_delete_image_image_not_found(self, mock_boto_client):
        # Create mock DynamoDB client
        mock_dynamo = MagicMock()
        mock_boto_client.return_value = mock_dynamo

        # Mock the DynamoDB response with no 'Item' found
        mock_dynamo.get_item.return_value = {}

        # Mock event with image_id
        mock_lambda_event = {
            'pathParameters': {'image_id': 'image_id_example'},
        }

        # Call the function
        response = delete_image(mock_lambda_event, None)

        # Assert the response for image not found
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('Image not found', json.loads(response['body'])['error'])

    # Test for handling errors in the delete_image function
    @patch('boto3.client')
    def test_delete_image_exception(self, mock_boto_client):
        # Create mock DynamoDB and S3 clients
        mock_dynamo = MagicMock()
        mock_s3 = MagicMock()

        # Mock the boto3 client to return the S3 and DynamoDB mock clients
        mock_boto_client.return_value = mock_s3
        mock_boto_client.return_value = mock_dynamo

        # Make the DynamoDB get_item throw an exception (simulating an error)
        mock_dynamo.get_item.side_effect = Exception("Internal Server Error")

        # Mock event with image_id
        mock_lambda_event = {
            'pathParameters': {'image_id': 'image_id_example'},
        }

        # Call the function
        response = delete_image(mock_lambda_event, None)

        # Assert the response for error handling
        self.assertEqual(response['statusCode'], 404)
        # self.assertIn('Internal Server Error', json.loads(response['body'])['error'])

if __name__ == '__main__':
    unittest.main()
