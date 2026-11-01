"""Base class for all API service classes."""

import logging
from typing import Any, Optional

import requests

from features.utils.config_manager import get_config
from features.utils.log_manager import get_logger
from features.utils.token_cache import get_token_cache


class APIBaseClass:
    """Base class for all API service classes."""

    def __init__(self, user_type: str = "default") -> None:
        """
        Initialize API service.

        :param user_type: User type for credential resolution
        """
        self.logger = get_logger()
        self.config = get_config()
        self.user_type = user_type
        self.base_url = self.config.env_config.get("api_base_url", "")
        self.token_cache = get_token_cache()
        self.session = requests.Session()

    def get_headers(self) -> dict:
        """
        Get request headers with authentication.

        :return: Dictionary of headers
        """
        headers = {"Content-Type": "application/json"}

        # Add bearer token if available
        token = self.token_cache.get_token(self.user_type)
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def get(self, endpoint: str, params: Optional[dict] = None, **kwargs) -> requests.Response:
        """
        Perform a GET request.

        :param endpoint: API endpoint path
        :param params: Query parameters
        :return: Response object
        """
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"GET {url}")
        response = self.session.get(url, headers=self.get_headers(), params=params, **kwargs)
        self.logger.info(f"Response status: {response.status_code}")
        return response

    def post(self, endpoint: str, json: Optional[dict] = None, **kwargs) -> requests.Response:
        """
        Perform a POST request.

        :param endpoint: API endpoint path
        :param json: JSON body
        :return: Response object
        """
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"POST {url} with body: {json}")
        response = self.session.post(url, headers=self.get_headers(), json=json, **kwargs)
        self.logger.info(f"Response status: {response.status_code}")
        return response

    def put(self, endpoint: str, json: Optional[dict] = None, **kwargs) -> requests.Response:
        """
        Perform a PUT request.

        :param endpoint: API endpoint path
        :param json: JSON body
        :return: Response object
        """
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"PUT {url} with body: {json}")
        response = self.session.put(url, headers=self.get_headers(), json=json, **kwargs)
        self.logger.info(f"Response status: {response.status_code}")
        return response

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Perform a DELETE request.

        :param endpoint: API endpoint path
        :return: Response object
        """
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"DELETE {url}")
        response = self.session.delete(url, headers=self.get_headers(), **kwargs)
        self.logger.info(f"Response status: {response.status_code}")
        return response
