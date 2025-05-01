import pytest
import requests
from unittest.mock import Mock
import sys
import os


from new_idea.utils.api_utils import get_movie_info

mock_json = {
    "results": [
        {"title": "Inception", "year": 2010}
    ]
}

#Simulates a successful API call using requests.get
@pytest.fixture
def mock_movie_api_success(mocker):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = mock_json
    mock_response.text = str(mock_json)
    mocker.patch("utils.api_utils.requests.get", return_value=mock_response)
    return mock_response

#Test successful API call
def test_get_movie_info_success(mock_movie_api_success):
    result = get_movie_info("Inception")
    assert result == mock_json
    mock_movie_api_success.raise_for_status.assert_called_once()

#Test request failures
def test_get_movie_info_request_failure(mocker):
    mocker.patch("utils.api_utils.requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to imdb232.p.rapidapi.com failed: Connection error"):
        get_movie_info("Inception")

#Test timeouts
def test_get_movie_info_timeout(mocker):
    mocker.patch("utils.api_utils.requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to imdb232.p.rapidapi.com timed out."):
        get_movie_info("Inception")