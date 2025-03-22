import pytest
import json
from unittest.mock import patch, MagicMock
from src.list_images import list_images

@pytest.fixture
def mock_lambda_event():
    return {
        'queryStringParameters': {'tag': 'nature', 'user_id': '123'},
    }

@patch('boto3.client')
def test_list_images(mock_boto_client, mock_lambda_event):
    mock_dynamo = MagicMock()
    mock_boto_client.return_value = mock_dynamo
    mock_dynamo.scan.return_value = {'Items': [{'ImageID': {'S': 'image_id_example'}, 'Metadata': {'S': json.dumps({'user_id': '123', 'tag': 'nature'})}}]}
    
    response = list_images(mock_lambda_event, None)
    
    assert response['statusCode'] == 200
    assert len(json.loads(response['body'])['images']) > 0
