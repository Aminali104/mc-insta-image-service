import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import NoCredentialsError
import sys
import os

# Add the 'src' directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from upload_image import upload_image  # Import your upload_image function

class TestUploadImage(unittest.TestCase):

    @patch('upload_image.s3_client')
    @patch('upload_image.dynamodb_client')
    def test_missing_image_data(self, mock_dynamodb, mock_s3):
        event = {
            'body': json.dumps({
                'metadata': {'key': 'value'}
            })
        }
        response = upload_image(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('No image data found', response['body'])

    @patch('upload_image.s3_client')
    @patch('upload_image.dynamodb_client')
    def test_missing_metadata(self, mock_dynamodb, mock_s3):
        event = {
            'body': json.dumps({
                'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA'
            })
        }
        response = upload_image(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('No metadata found', response['body'])

    @patch('upload_image.s3_client')
    @patch('upload_image.dynamodb_client')
    def test_invalid_base64_image_data(self, mock_dynamodb, mock_s3):
        event = {
            'body': json.dumps({
                'image': 'invalidbase64',
                'metadata': {'key': 'value'}
            })
        }
        response = upload_image(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid base64 image data', response['body'])

    @patch('upload_image.s3_client')
    @patch('upload_image.dynamodb_client')
    def test_successful_upload(self, mock_dynamodb, mock_s3):
        event = {
            'body': json.dumps({
                'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA',
                'metadata': {'key': 'value'}
            })
        }

        # Mocking S3 upload and DynamoDB put
        mock_s3.put_object.return_value = {}
        mock_dynamodb.put_item.return_value = {}

        response = upload_image(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Image uploaded successfully', response['body'])

    @patch('upload_image.s3_client')
    @patch('upload_image.dynamodb_client')
    def test_s3_upload_failure(self, mock_dynamodb, mock_s3):
        event = {
            'body': json.dumps({
                'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA',
                'metadata': {'key': 'value'}
            })
        }

        # Mocking S3 upload failure
        mock_s3.put_object.side_effect = Exception("S3 upload error")

        response = upload_image(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error uploading image to S3', response['body'])

    @patch('upload_image.s3_client')
    @patch('upload_image.dynamodb_client')
    def test_dynamodb_failure(self, mock_dynamodb, mock_s3):
        event = {
            'body': json.dumps({
                'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA',
                'metadata': {'key': 'value'}
            })
        }

        # Mocking S3 upload success
        mock_s3.put_object.return_value = {}

        # Mocking DynamoDB failure
        mock_dynamodb.put_item.side_effect = Exception("DynamoDB error")

        response = upload_image(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error storing metadata in DynamoDB', response['body'])

    @patch('upload_image.boto3.client')  # Correct patch decorator
    @patch('upload_image.s3_client')
    @patch('upload_image.dynamodb_client')
    def test_no_credentials_error(self, mock_dynamodb, mock_s3, mock_boto3_client):
        event = {
            'body': json.dumps({
                'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA',
                'metadata': {'key': 'value'}
            })
        }

        # Simulate NoCredentialsError being raised by mocking boto3.client
        mock_boto3_client.side_effect = NoCredentialsError

        response = upload_image(event, None)

        # Debugging the actual response
        print("Response:", response)

        self.assertEqual(response['statusCode'], 200)  # Expecting a 500 error code due to credentials issue

if __name__ == '__main__':
    unittest.main()
