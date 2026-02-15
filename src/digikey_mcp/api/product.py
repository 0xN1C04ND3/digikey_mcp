"""Product operations for DigiKey API."""

from typing import Dict, Any


def search_product_substitutions(
    client,
    product_number: str,
    limit: int = 10,
    search_options: str = None,
    exclude_marketplace: bool = False,
) -> Dict[str, Any]:
    """Search for product substitutions for a given product.

    Args:
        client: DigiKey client instance
        product_number: The product to get substitutions for
        limit: Number of substitutions (default: 10)
        search_options: Filters like LeadFree,RoHSCompliant,InStock
        exclude_marketplace: Exclude marketplace products (default: False)

    Returns:
        API response dictionary with substitution products
    """
    url = f"{client.api_base}/products/v4/search/{product_number}/substitutions"
    headers = client.get_headers()

    params = {"limit": limit, "excludeMarketPlaceProducts": exclude_marketplace}
    if search_options:
        params["searchOptionList"] = search_options

    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return client.make_request("GET", url, headers)


def get_product_media(client, product_number: str) -> Dict[str, Any]:
    """Get media (images, documents, videos) for a product.

    Args:
        client: DigiKey client instance
        product_number: The product to get media for

    Returns:
        API response dictionary with product media
    """
    url = f"{client.api_base}/products/v4/search/{product_number}/media"
    headers = client.get_headers()
    return client.make_request("GET", url, headers)


def get_product_pricing(
    client,
    product_number: str,
    customer_id: str = "0",
    requested_quantity: int = 1,
) -> Dict[str, Any]:
    """Get detailed pricing information for a product.

    Args:
        client: DigiKey client instance
        product_number: The product to get pricing for
        customer_id: Customer ID for pricing (default: "0")
        requested_quantity: Quantity for pricing calculation (default: 1)

    Returns:
        API response dictionary with pricing information
    """
    url = f"{client.api_base}/products/v4/search/{product_number}/productpricing"
    headers = client.get_headers(customer_id)

    params = {"requestedQuantity": requested_quantity}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return client.make_request("GET", url, headers)


def get_digi_reel_pricing(
    client,
    product_number: str,
    requested_quantity: int,
    customer_id: str = "0",
) -> Dict[str, Any]:
    """Get DigiReel pricing for a product.

    Args:
        client: DigiKey client instance
        product_number: DigiKey product number (must be DigiReel compatible)
        requested_quantity: Quantity for DigiReel pricing
        customer_id: Customer ID for pricing (default: "0")

    Returns:
        API response dictionary with DigiReel pricing
    """
    url = f"{client.api_base}/products/v4/search/{product_number}/digireelpricing"
    headers = client.get_headers(customer_id)

    params = {"requestedQuantity": requested_quantity}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return client.make_request("GET", url, headers)
