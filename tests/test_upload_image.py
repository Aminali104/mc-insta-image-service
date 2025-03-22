import pytest
import json
from unittest.mock import patch, MagicMock
from src.upload_image import upload_image

@pytest.fixture
def mock_lambda_event():
    return {
        'body': json.dumps({'image': 'image_data', 'metadata': {'user_id': '123', 'tag': 'nature'}}),
    }

@patch('boto3.client')
def test_upload_image(mock_boto_client, mock_lambda_event):
    mock_s3 = MagicMock()
    mock_dynamo = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_boto_client.return_value = mock_dynamo

    response = upload_image(mock_lambda_event, None)
    
    assert response['statusCode'] == 200
    assert 'Image uploaded successfully' in json.loads(response['body'])['message']
