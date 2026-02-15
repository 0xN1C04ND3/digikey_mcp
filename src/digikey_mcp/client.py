"""DigiKey API client with OAuth2 authentication."""

import logging
import os
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DigiKeyClient:
    """DigiKey API client with OAuth2 authentication."""

    def __init__(self, client_id: str, client_secret: str, use_sandbox: bool = False):
        """Initialize DigiKey client.

        Args:
            client_id: DigiKey OAuth2 client ID
            client_secret: DigiKey OAuth2 client secret
            use_sandbox: Use sandbox environment (default: False)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.use_sandbox = use_sandbox

        if use_sandbox:
            self.token_url = "https://sandbox-api.digikey.com/v1/oauth2/token"
            self.api_base = "https://sandbox-api.digikey.com"
        else:
            self.token_url = "https://api.digikey.com/v1/oauth2/token"
            self.api_base = "https://api.digikey.com"

        self.access_token = None

    def authenticate(self) -> None:
        """Get OAuth2 access token from DigiKey."""
        if not self.client_id or not self.client_secret:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be provided")

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        endpoint = "SANDBOX" if self.use_sandbox else "PRODUCTION"
        logger.info(
            f"Requesting token from {endpoint} with CLIENT_ID: {self.client_id[:10]}..."
        )
        resp = requests.post(self.token_url, data=data, headers=headers)

        if resp.status_code != 200:
            logger.error(f"OAuth error: {resp.status_code} - {resp.text}")
            resp.raise_for_status()

        self.access_token = resp.json()["access_token"]
        logger.info("Successfully obtained access token")

    def get_headers(self, customer_id: str = "0") -> Dict[str, str]:
        """Get standard headers for DigiKey API requests.

        Args:
            customer_id: Customer ID for API requests

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "X-DIGIKEY-Client-Id": self.client_id,
            "Content-Type": "application/json",
            "X-DIGIKEY-Locale-Site": "US",
            "X-DIGIKEY-Locale-Language": "en",
            "X-DIGIKEY-Locale-Currency": "USD",
            "X-DIGIKEY-Customer-Id": customer_id,
        }

    def make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make an API request with error handling and logging.

        Args:
            method: HTTP method (GET or POST)
            url: Full URL for the request
            headers: HTTP headers
            data: Optional request body data

        Returns:
            JSON response data

        Raises:
            requests.HTTPError: If the request fails
        """
        logger.info(f"Making {method} request to {url}")
        logger.debug(
            f"Headers: {', '.join([f'{k}: {v}' for k, v in headers.items() if 'Authorization' not in k])}"
        )
        if data:
            logger.debug(f"Request body: {data}")

        if method.upper() == "GET":
            resp = requests.get(url, headers=headers)
        else:
            resp = requests.post(url, headers=headers, json=data)

        logger.info(f"Response status: {resp.status_code}")
        if resp.status_code != 200:
            logger.error(f"API error: {resp.status_code} - {resp.text}")
            resp.raise_for_status()

        return resp.json()
