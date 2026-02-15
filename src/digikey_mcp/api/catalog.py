"""Catalog operations for DigiKey API."""

from typing import Dict, Any


def search_manufacturers(client) -> Dict[str, Any]:
    """Search and retrieve all product manufacturers.

    Args:
        client: DigiKey client instance

    Returns:
        API response dictionary with manufacturer list
    """
    url = f"{client.api_base}/products/v4/search/manufacturers"
    headers = client.get_headers()
    return client.make_request("GET", url, headers)


def search_categories(client) -> Dict[str, Any]:
    """Search and retrieve all product categories.

    Args:
        client: DigiKey client instance

    Returns:
        API response dictionary with category list
    """
    url = f"{client.api_base}/products/v4/search/categories"
    headers = client.get_headers()
    return client.make_request("GET", url, headers)


def get_category_by_id(client, category_id: int) -> Dict[str, Any]:
    """Get specific category details by ID.

    Args:
        client: DigiKey client instance
        category_id: The category ID to retrieve

    Returns:
        API response dictionary with category details
    """
    url = f"{client.api_base}/products/v4/search/categories/{category_id}"
    headers = client.get_headers()
    return client.make_request("GET", url, headers)
