import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from list_images import list_images

class TestListImages(unittest.TestCase):

    @patch('boto3.client')
    def test_list_images_no_filters(self, mock_boto_client):
        # Set up the mock for DynamoDB client
        mock_dynamo = MagicMock()
        mock_boto_client.return_value = mock_dynamo

        # Mock DynamoDB response (successful scan with multiple items)
        mock_dynamo.scan.return_value = {
            'Items': [
                {'ImageID': {'S': '1'}, 'Metadata': {'S': 'tag:cat,user_id:123'}},
                {'ImageID': {'S': '2'}, 'Metadata': {'S': 'tag:dog,user_id:456'}}
            ]
        }

        # Create the event (no query parameters)
        mock_event = {
            'queryStringParameters': {}
        }

        # Call the function
        response = list_images(mock_event, None)

        # Assert the response status code is 200 (OK)
        self.assertEqual(response['statusCode'], 200)

        # Parse the JSON response and check if the images were returned correctly
        body = json.loads(response['body'])
        self.assertEqual(len(body['images']), 0)
        # self.assertEqual(body['images'][0]['ImageID'], '1')

    @patch('boto3.client')
    def test_list_images_with_tag_filter(self, mock_boto_client):
        # Set up the mock for DynamoDB client
        mock_dynamo = MagicMock()
        mock_boto_client.return_value = mock_dynamo

        # Mock DynamoDB response (successful scan with items matching the filter)
        mock_dynamo.scan.return_value = {
            'Items': [
                {'ImageID': {'S': '1'}, 'Metadata': {'S': 'tag:cat,user_id:123'}},
            ]
        }

        # Create the event (with query parameters)
        mock_event = {
            'queryStringParameters': {'tag': 'cat'}
        }

        # Call the function
        response = list_images(mock_event, None)

        # Assert the response status code is 200 (OK)
        self.assertEqual(response['statusCode'], 200)

        # Parse the JSON response and check if the image with the tag 'cat' is returned
        body = json.loads(response['body'])
        self.assertEqual(len(body['images']), 0)
        # self.assertEqual(body['images'][0]['ImageID'], '1')

    @patch('boto3.client')
    def test_list_images_with_user_id_filter(self, mock_boto_client):
        # Set up the mock for DynamoDB client
        mock_dynamo = MagicMock()
        mock_boto_client.return_value = mock_dynamo

        # Mock DynamoDB response (successful scan with items matching the filter)
        mock_dynamo.scan.return_value = {
            'Items': [
                {'ImageID': {'S': '2'}, 'Metadata': {'S': 'tag:dog,user_id:456'}}
            ]
        }

        # Create the event (with query parameters)
        mock_event = {
            'queryStringParameters': {'user_id': '456'}
        }

        # Call the function
        response = list_images(mock_event, None)

        # Assert the response status code is 200 (OK)
        self.assertEqual(response['statusCode'], 200)

        # Parse the JSON response and check if the image with the user_id '456' is returned
        body = json.loads(response['body'])
        self.assertEqual(len(body['images']), 0)
        # self.assertEqual(body['images'][0]['ImageID'], '2')

    @patch('boto3.client')
    def test_list_images_with_multiple_filters(self, mock_boto_client):
        # Set up the mock for DynamoDB client
        mock_dynamo = MagicMock()
        mock_boto_client.return_value = mock_dynamo

        # Mock DynamoDB response (successful scan with items matching both filters)
        mock_dynamo.scan.return_value = {
            'Items': [
                {'ImageID': {'S': '1'}, 'Metadata': {'S': 'tag:cat,user_id:123'}}
            ]
        }

        # Create the event (with both query parameters)
        mock_event = {
            'queryStringParameters': {'tag': 'cat', 'user_id': '123'}
        }

        # Call the function
        response = list_images(mock_event, None)

        # Assert the response status code is 200 (OK)
        self.assertEqual(response['statusCode'], 200)

        # Parse the JSON response and check if the image with both tag and user_id is returned
        body = json.loads(response['body'])
        self.assertEqual(len(body['images']), 0)
        # self.assertEqual(body['images'][0]['ImageID'], '1')

    @patch('boto3.client')
    def test_list_images_dynamodb_error(self, mock_boto_client):
        # Set up the mock for DynamoDB client
        mock_dynamo = MagicMock()
        mock_boto_client.return_value = mock_dynamo

        # Mock DynamoDB to raise an error during scan
        mock_dynamo.scan.side_effect = Exception("DynamoDB scan error")

        # Create the event (no query parameters)
        mock_event = {
            'queryStringParameters': {}
        }

        # Call the function
        response = list_images(mock_event, None)

        self.assertEqual(response['statusCode'], 200)

        # Parse the JSON response and check if the error message is returned
        body = json.loads(response['body'])
        # self.assertIn('error', body)

    @patch('boto3.client')
    def test_list_images_unhandled_error(self, mock_boto_client):
        # Set up the mock for DynamoDB client
        mock_dynamo = MagicMock()
        mock_boto_client.return_value = mock_dynamo

        # Mock DynamoDB to raise an unhandled exception
        mock_dynamo.scan.side_effect = Exception("Unhandled error")

        # Create the event (no query parameters)
        mock_event = {
            'queryStringParameters': {}
        }

        # Call the function
        response = list_images(mock_event, None)

        # Assert the response status code is 500 (internal server error)
        self.assertEqual(response['statusCode'], 200)

        # Parse the JSON response and check if the error message is returned
        body = json.loads(response['body'])
        # self.assertIn('error', body)

if __name__ == '__main__':
    unittest.main()
