"""MCP client tests for search tools (mocked API)."""

import json

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_keyword_search_via_mcp(mcp_server_with_mock_client):
    """Test keyword search operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "keyword_search_tool", {"keywords": "Arduino", "limit": 5}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "SearchResults" in data
        assert "Products" in data["SearchResults"]
        assert isinstance(data["SearchResults"]["Products"], list)
        assert len(data["SearchResults"]["Products"]) > 0


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_product_details_via_mcp(mcp_server_with_mock_client):
    """Test product details operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "product_details_tool", {"product_number": "TEST-001"}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "DigiKeyProductNumber" in data
        assert data["DigiKeyProductNumber"] == "TEST-001"


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_search_manufacturers_via_mcp(mcp_server_with_mock_client):
    """Test search manufacturers operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("search_manufacturers_tool", {})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "Manufacturers" in data
        assert isinstance(data["Manufacturers"], list)


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_search_categories_via_mcp(mcp_server_with_mock_client):
    """Test search categories operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("search_categories_tool", {})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "Categories" in data
        assert isinstance(data["Categories"], list)


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_get_category_by_id_via_mcp(mcp_server_with_mock_client):
    """Test get category by ID operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("get_category_by_id_tool", {"category_id": 1})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "Categories" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_search_product_substitutions_via_mcp(mcp_server_with_mock_client):
    """Test search product substitutions via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "search_product_substitutions_tool",
            {"product_number": "TEST-001", "limit": 10},
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "Substitutions" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_get_product_media_via_mcp(mcp_server_with_mock_client):
    """Test get product media via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "get_product_media_tool", {"product_number": "TEST-001"}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "Media" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_get_product_pricing_via_mcp(mcp_server_with_mock_client):
    """Test get product pricing via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "get_product_pricing_tool",
            {"product_number": "TEST-001", "requested_quantity": 1},
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "ProductPricing" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_get_digi_reel_pricing_via_mcp(mcp_server_with_mock_client):
    """Test get DigiReel pricing via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "get_digi_reel_pricing_tool",
            {"product_number": "TEST-001", "requested_quantity": 100},
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "DigiReelPricing" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_tool_registration(mcp_server_with_mock_client):
    """Test that all tools are properly registered with correct schema."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        tools = await client.list_tools()

        tool_names = [tool.name for tool in tools]

        # Check that all expected tools are registered
        expected_tools = [
            "keyword_search_tool",
            "product_details_tool",
            "search_manufacturers_tool",
            "search_categories_tool",
            "get_category_by_id_tool",
            "search_product_substitutions_tool",
            "get_product_media_tool",
            "get_product_pricing_tool",
            "get_digi_reel_pricing_tool",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} not found"

        # Verify keyword_search_tool has correct schema
        search_tool = next(t for t in tools if t.name == "keyword_search_tool")
        assert search_tool.inputSchema is not None

        schema = search_tool.inputSchema
        properties = schema.get("properties", {})
        assert "keywords" in properties
        assert "limit" in properties


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_keyword_search_with_filters(mcp_server_with_mock_client):
    """Test keyword search with additional filters via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "keyword_search_tool",
            {
                "keywords": "resistor",
                "limit": 10,
                "search_options": "InStock,RoHSCompliant",
            },
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_keyword_search_with_sorting(mcp_server_with_mock_client):
    """Test keyword search with sorting via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "keyword_search_tool",
            {
                "keywords": "capacitor",
                "limit": 5,
                "sort_field": "Price",
                "sort_order": "Ascending",
            },
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0
