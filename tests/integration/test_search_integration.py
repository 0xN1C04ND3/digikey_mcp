"""Integration tests for search with real DigiKey API."""

import json
import os

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.utilities.tests import run_server_async


def is_integration_configured():
    """Check if integration tests can run."""
    return bool(os.getenv("CLIENT_ID") and os.getenv("CLIENT_SECRET"))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_keyword_search_real_api():
    """Test keyword search with real DigiKey API."""
    if not is_integration_configured():
        pytest.skip("CLIENT_ID and CLIENT_SECRET must be set for integration tests")

    os.environ.setdefault("CLIENT_ID", os.getenv("CLIENT_ID", ""))
    os.environ.setdefault("CLIENT_SECRET", os.getenv("CLIENT_SECRET", ""))

    from digikey_mcp import server

    async with run_server_async(server.mcp) as url:
        async with Client(StreamableHttpTransport(url)) as client:
            result = await client.call_tool(
                "keyword_search_tool", {"keywords": "Arduino", "limit": 5}
            )

            assert result is not None
            assert hasattr(result, "content")
            assert len(result.content) > 0

            data = json.loads(result.content[0].text)
            print(
                f"✓ Search returned results: {data.get('SearchResults', {}).get('Products', []).__len__()} products"
            )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_product_details_real_api():
    """Test product details with real DigiKey API."""
    if not is_integration_configured():
        pytest.skip("CLIENT_ID and CLIENT_SECRET must be set for integration tests")

    os.environ.setdefault("CLIENT_ID", os.getenv("CLIENT_ID", ""))
    os.environ.setdefault("CLIENT_SECRET", os.getenv("CLIENT_SECRET", ""))

    from digikey_mcp import server

    async with run_server_async(server.mcp) as url:
        async with Client(StreamableHttpTransport(url)) as client:
            result = await client.call_tool(
                "product_details_tool", {"product_number": "296-1721-1-ND"}
            )

            assert result is not None
            assert hasattr(result, "content")
            assert len(result.content) > 0

            data = json.loads(result.content[0].text)
            print(f"✓ Got product details: {data.get('DigiKeyProductNumber', 'N/A')}")
