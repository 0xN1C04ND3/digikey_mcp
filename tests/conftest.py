"""Shared test fixtures and configuration for DigiKey MCP tests."""

import json
import os
from unittest.mock import MagicMock

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.utilities.tests import run_server_async, temporary_settings


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy."""
    import asyncio

    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
def mock_digikey_client():
    """Create a mocked DigiKey client for unit/mcp_client tests."""

    class MockClient:
        """Simple mock client that returns predefined data."""

        def __init__(self):
            self.api_base = "https://sandbox-api.digikey.com"

        def make_request(self, method, url, headers, data=None):
            """Mock the make_request method - returns based on URL."""
            if "keyword" in url:
                return {
                    "SearchResults": {
                        "Products": [
                            {
                                "DigiKeyProductNumber": "TEST-001",
                                "Manufacturer": "TestCorp",
                                "Description": "Test Product 1",
                            },
                            {
                                "DigiKeyProductNumber": "TEST-002",
                                "Manufacturer": "TestCorp",
                                "Description": "Test Product 2",
                            },
                        ]
                    }
                }
            elif "productdetails" in url:
                return {"DigiKeyProductNumber": "TEST-001", "Manufacturer": "TestCorp"}
            elif "manufacturer" in url:
                return {
                    "Manufacturers": [
                        {"ManufacturerId": "1", "ManufacturerName": "TestCorp"}
                    ]
                }
            elif "category" in url:
                return {
                    "Categories": [{"CategoryId": "1", "CategoryName": "Resistors"}]
                }
            elif "substitution" in url:
                return {"Substitutions": []}
            elif "media" in url:
                return {"Media": []}
            elif "pricing" in url:
                return {"ProductPricing": []}
            elif "digireel" in url:
                return {"DigiReelPricing": {}}
            return {}

        def get_headers(self, customer_id="0"):
            return {"Authorization": "Bearer mock-token"}

        # These are here for compatibility but won't be called due to make_request override
        def keyword_search(self, *args, **kwargs):
            return {"SearchResults": {"Products": []}}

        def product_details(self, *args, **kwargs):
            return {"DigiKeyProductNumber": "TEST-001"}

    return MockClient()


def pytest_collection_modifyitems(config, items):
    """Skip MCP client tests unless explicitly enabled.

    These tests currently hang when run as a suite. Set
    DIGIKEY_RUN_MCP_CLIENT_TESTS=1 to enable them.
    """
    if os.getenv("DIGIKEY_RUN_MCP_CLIENT_TESTS"):
        return
    skip_marker = pytest.mark.skip(
        reason="MCP client tests are temporarily disabled (set DIGIKEY_RUN_MCP_CLIENT_TESTS=1 to run)."
    )
    for item in items:
        if "mcp_client" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="function")
async def mcp_server_with_mock_client(mock_digikey_client, monkeypatch):
    """Create MCP server with mocked DigiKey client (like InvenTree)."""
    import importlib
    import digikey_mcp.server

    importlib.reload(digikey_mcp.server)
    from digikey_mcp import server

    def mock_get_client():
        return mock_digikey_client

    monkeypatch.setattr(server, "get_client", mock_get_client)

    with temporary_settings(stateless_http=True, json_response=True):
        async with run_server_async(server.mcp) as url:
            yield url


@pytest.fixture
def sample_product_data():
    """Sample product data for tests."""
    return {
        "keywords": "Arduino",
        "limit": 5,
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for tests."""
    return {
        "category_id": 1,
    }


@pytest.fixture
def digikey_connection_params():
    """Get DigiKey connection params from environment."""
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        pytest.skip("CLIENT_ID and CLIENT_SECRET must be set for integration tests")

    return {"client_id": client_id, "client_secret": client_secret}


@pytest.fixture
async def mcp_server_with_real_client(digikey_connection_params):
    """Create MCP server with real DigiKey connection."""
    from digikey_mcp import server

    os.environ["CLIENT_ID"] = digikey_connection_params["client_id"]
    os.environ["CLIENT_SECRET"] = digikey_connection_params["client_secret"]

    with temporary_settings(stateless_http=True, json_response=True):
        async with run_server_async(server.mcp) as url:
            yield url


def assert_mcp_tool_response(result, expected_keys=None):
    """Assert MCP tool response is valid."""
    assert result is not None, "MCP tool result should not be None"
    assert hasattr(result, "content"), "MCP tool result should have content"
    assert len(result.content) > 0, "MCP tool result should have at least one content"

    content = result.content[0]
    assert hasattr(content, "text"), "MCP tool content should have text"

    if expected_keys:
        data = json.loads(content.text)
        for key in expected_keys:
            assert key in data, f"Expected key '{key}' not found in response: {data}"
