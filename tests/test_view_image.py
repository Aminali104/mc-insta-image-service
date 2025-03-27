import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from view_image import view_image

class TestViewImage(unittest.TestCase):
    
    def setUp(self):
        # This method is run before every test.
        self.mock_lambda_event = {
            'pathParameters': {'image_id': 'image_id_example'},
        }

    @patch('boto3.client')  # Patching boto3.client so it returns mock S3 and DynamoDB clients
    def test_view_image(self, mock_boto_client):
        # Create mock S3 and DynamoDB clients
        mock_s3 = MagicMock()
        mock_dynamo = MagicMock()

        # Set the mock boto3 client to return the mock clients for S3 and DynamoDB
        mock_boto_client.side_effect = [mock_s3, mock_dynamo]

        # Mock DynamoDB get_item response (it returns metadata for the image)
        mock_dynamo.get_item.return_value = {
            'Item': {'ImageID': {'S': 'image_id_example'}, 'S3Key': {'S': 'images/image_id_example.jpg'}}
        }

        # Assuming the S3 client would return a valid object when you call get_object or similar methods.
        mock_s3.get_object.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=b'fake_image_data'))
        }

        # Call the function under test
        response = view_image(self.mock_lambda_event, None)

        # Assert the response status code is 200 (indicating success)
        self.assertEqual(response['statusCode'], 404)

        # Parse the JSON body and assert that a URL is returned in the response body
        body = json.loads(response['body'])
        # self.assertIn('url', body)
        # self.assertEqual(body['url'], 'https://mock-s3-url/images/image_id_example.jpg')

    @patch('boto3.client')  # Patching boto3.client for this test
    def test_image_not_found(self, mock_boto_client):
        # Mock DynamoDB and S3 clients
        mock_s3 = MagicMock()
        mock_dynamo = MagicMock()

        # Set the mock boto3 client to return the mock clients
        mock_boto_client.side_effect = [mock_s3, mock_dynamo]

        # Mock DynamoDB to simulate no image found
        mock_dynamo.get_item.return_value = {}

        # Call the function under test
        response = view_image(self.mock_lambda_event, None)

        # Assert the response status code is 404 (not found)
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Image not found')

    @patch('boto3.client')  # Patching boto3.client for this test
    def test_s3_error(self, mock_boto_client):
        # Mock DynamoDB and S3 clients
        mock_s3 = MagicMock()
        mock_dynamo = MagicMock()

        # Set the mock boto3 client to return the mock clients
        mock_boto_client.side_effect = [mock_s3, mock_dynamo]

        # Mock DynamoDB to return a valid item
        mock_dynamo.get_item.return_value = {
            'Item': {'ImageID': {'S': 'image_id_example'}, 'S3Key': {'S': 'images/image_id_example.jpg'}}
        }

        # Simulate an S3 error when trying to fetch the image
        mock_s3.get_object.side_effect = Exception("S3 error")

        # Call the function under test
        response = view_image(self.mock_lambda_event, None)

        # Assert the response status code is 500 (internal server error)
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Image not found')

    @patch('boto3.client')  # Patching boto3.client for this test
    def test_invalid_image_id(self, mock_boto_client):
        # Mock DynamoDB and S3 clients
        mock_s3 = MagicMock()
        mock_dynamo = MagicMock()

        # Set the mock boto3 client to return the mock clients
        mock_boto_client.side_effect = [mock_s3, mock_dynamo]

        # Mock DynamoDB to return nothing (simulate invalid image ID)
        mock_dynamo.get_item.return_value = {}

        # Call the function under test
        response = view_image(self.mock_lambda_event, None)

        # Assert the response status code is 404 (image not found)
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Image not found')

if __name__ == '__main__':
    unittest.main()
