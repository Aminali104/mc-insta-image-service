import pytest
import json
from unittest.mock import patch, MagicMock
from src.delete_image import delete_image

@pytest.fixture
def mock_lambda_event():
    return {
        'pathParameters': {'image_id': 'image_id_example'},
    }

@patch('boto3.client')
def test_delete_image(mock_boto_client, mock_lambda_event):
    mock_dynamo = MagicMock()
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_boto_client.return_value = mock_dynamo

    mock_dynamo.get_item.return_value = {
        'Item': {'ImageID': {'S': 'image_id_example'}, 'S3Key': {'S': 'images/image_id_example.jpg'}}
    }
    
    response = delete_image(mock_lambda_event, None)
    
    assert response['statusCode'] == 200
    assert 'Image deleted successfully' in json.loads(response['body'])['message']
