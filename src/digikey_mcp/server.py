#!/usr/bin/env python3
"""DigiKey MCP Server - Model Context Protocol server for DigiKey Product Search API."""

import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .client import DigiKeyClient
from .api import (
    keyword_search,
    product_details,
    search_manufacturers,
    search_categories,
    get_category_by_id,
    search_product_substitutions,
    get_product_media,
    get_product_pricing,
    get_digi_reel_pricing,
)

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("DigiKey MCP Server")

# Initialize and authenticate DigiKey client at startup
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USE_SANDBOX = os.getenv("USE_SANDBOX", "false").lower() == "true"

logger.info("=== STARTING DIGIKEY MCP SERVER ===")
client = DigiKeyClient(CLIENT_ID, CLIENT_SECRET, USE_SANDBOX)
client.authenticate()
logger.info("=== SERVER READY ===")


# ═══════════════════════════════════════════════════════════════════════
# Health Endpoint
# ═══════════════════════════════════════════════════════════════════════


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request):
    """Health check endpoint."""
    return JSONResponse({"status": "ok", "service": "digikey-mcp"})


# ═══════════════════════════════════════════════════════════════════════
# MCP Tool Definitions
# ═══════════════════════════════════════════════════════════════════════


@mcp.tool()
def keyword_search_tool(
    keywords: str,
    limit: int = 5,
    manufacturer_id: str = None,
    category_id: str = None,
    search_options: str = None,
    sort_field: str = None,
    sort_order: str = "Ascending",
):
    """Search DigiKey products by keyword.

    Args:
        keywords: Search terms or part numbers
        limit: Maximum number of results (default: 5)
        manufacturer_id: Filter by specific manufacturer ID
        category_id: Filter by specific category ID
        search_options: Comma-delimited filters like LeadFree,RoHSCompliant,InStock
        sort_field: Field to sort by. Options: None, Packaging, ProductStatus, DigiKeyProductNumber, ManufacturerProductNumber, Manufacturer, MinimumQuantity, QuantityAvailable, Price, Supplier, PriceManufacturerStandardPackage
        sort_order: Sort direction - Ascending or Descending (default: Ascending)
    """
    return keyword_search(
        client,
        keywords,
        limit,
        manufacturer_id,
        category_id,
        search_options,
        sort_field,
        sort_order,
    )


@mcp.tool()
def product_details_tool(
    product_number: str, manufacturer_id: str = None, customer_id: str = "0"
):
    """Get detailed information for a specific product.

    Args:
        product_number: DigiKey or manufacturer part number
        manufacturer_id: Optional manufacturer ID for disambiguation
        customer_id: Customer ID for pricing (default: "0")
    """
    return product_details(client, product_number, manufacturer_id, customer_id)


@mcp.tool()
def search_manufacturers_tool():
    """Search and retrieve all product manufacturers."""
    return search_manufacturers(client)


@mcp.tool()
def search_categories_tool():
    """Search and retrieve all product categories."""
    return search_categories(client)


@mcp.tool()
def get_category_by_id_tool(category_id: int):
    """Get specific category details by ID.

    Args:
        category_id: The category ID to retrieve
    """
    return get_category_by_id(client, category_id)


@mcp.tool()
def search_product_substitutions_tool(
    product_number: str,
    limit: int = 10,
    search_options: str = None,
    exclude_marketplace: bool = False,
):
    """Search for product substitutions for a given product.

    Args:
        product_number: The product to get substitutions for
        limit: Number of substitutions (default: 10)
        search_options: Filters like LeadFree,RoHSCompliant,InStock
        exclude_marketplace: Exclude marketplace products (default: False)
    """
    return search_product_substitutions(
        client, product_number, limit, search_options, exclude_marketplace
    )


@mcp.tool()
def get_product_media_tool(product_number: str):
    """Get media (images, documents, videos) for a product.

    Args:
        product_number: The product to get media for
    """
    return get_product_media(client, product_number)


@mcp.tool()
def get_product_pricing_tool(
    product_number: str, customer_id: str = "0", requested_quantity: int = 1
):
    """Get detailed pricing information for a product.

    Args:
        product_number: The product to get pricing for
        customer_id: Customer ID for pricing (default: "0")
        requested_quantity: Quantity for pricing calculation (default: 1)
    """
    return get_product_pricing(client, product_number, customer_id, requested_quantity)


@mcp.tool()
def get_digi_reel_pricing_tool(
    product_number: str, requested_quantity: int, customer_id: str = "0"
):
    """Get DigiReel pricing for a product.

    Args:
        product_number: DigiKey product number (must be DigiReel compatible)
        requested_quantity: Quantity for DigiReel pricing
        customer_id: Customer ID for pricing (default: "0")
    """
    return get_digi_reel_pricing(
        client, product_number, requested_quantity, customer_id
    )


# ═══════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════


def main():
    """Main entry point for the DigiKey MCP server."""
    logger.info("Starting DigiKey MCP server")
    mcp.run()


if __name__ == "__main__":
    main()
