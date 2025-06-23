"""General tests for the RestAdapter class in ncei_access module."""

import unittest
import requests
from unittest.mock import patch, MagicMock
from ncei_access.rest_adapter import RestAdapter, NceiAccessException
from ncei_access.models import Result


class TestRestAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = RestAdapter()

    @patch("ncei_access.rest_adapter.requests.get")
    def test_get_success_data_endpoint(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.json.return_value = {"results": [{"foo": "bar"}]}
        mock_get.return_value = mock_response
        result = self.adapter.get(endpoint="data/v1/", ep_params={})
        self.assertIsInstance(result, Result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, {"results": [{"foo": "bar"}]})

    @patch("ncei_access.rest_adapter.requests.get")
    def test_get_success_search_endpoint(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.json.return_value = {"results": [{"foo": "baz"}]}
        mock_get.return_value = mock_response
        result = self.adapter.get(endpoint="search/v1/data", ep_params={})
        self.assertIsInstance(result, Result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, [{"foo": "baz"}])

    @patch("ncei_access.rest_adapter.requests.get")
    def test_get_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        with self.assertRaises(NceiAccessException):
            self.adapter.get(endpoint="data/v1/", ep_params={})

    @patch("ncei_access.rest_adapter.requests.get")
    def test_get_bad_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.json.side_effect = ValueError("Bad JSON")
        mock_get.return_value = mock_response
        with self.assertRaises(NceiAccessException):
            self.adapter.get(endpoint="data/v1/", ep_params={})


if __name__ == "__main__":
    unittest.main()
