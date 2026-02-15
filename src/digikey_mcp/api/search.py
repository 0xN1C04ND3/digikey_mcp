"""Search operations for DigiKey API."""

from typing import Dict, Any


def keyword_search(
    client,
    keywords: str,
    limit: int = 5,
    manufacturer_id: str = None,
    category_id: str = None,
    search_options: str = None,
    sort_field: str = None,
    sort_order: str = "Ascending",
) -> Dict[str, Any]:
    """Search DigiKey products by keyword.

    Args:
        client: DigiKey client instance
        keywords: Search terms or part numbers
        limit: Maximum number of results (default: 5)
        manufacturer_id: Filter by specific manufacturer ID
        category_id: Filter by specific category ID
        search_options: Comma-delimited filters like LeadFree,RoHSCompliant,InStock
        sort_field: Field to sort by
        sort_order: Sort direction - Ascending or Descending

    Returns:
        API response dictionary
    """
    url = f"{client.api_base}/products/v4/search/keyword"
    headers = client.get_headers()

    body = {"Keywords": keywords, "Limit": limit}

    if manufacturer_id:
        body["ManufacturerId"] = manufacturer_id
    if category_id:
        body["CategoryId"] = category_id
    if search_options:
        body["SearchOptionList"] = search_options.split(",")

    # Add sort options if specified
    if sort_field:
        body["SortOptions"] = {"Field": sort_field, "SortOrder": sort_order}

    return client.make_request("POST", url, headers, body)


def product_details(
    client, product_number: str, manufacturer_id: str = None, customer_id: str = "0"
) -> Dict[str, Any]:
    """Get detailed information for a specific product.

    Args:
        client: DigiKey client instance
        product_number: DigiKey or manufacturer part number
        manufacturer_id: Optional manufacturer ID for disambiguation
        customer_id: Customer ID for pricing (default: "0")

    Returns:
        API response dictionary
    """
    url = f"{client.api_base}/products/v4/search/{product_number}/productdetails"
    headers = client.get_headers(customer_id)

    params = {}
    if manufacturer_id:
        params["manufacturerId"] = manufacturer_id

    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return client.make_request("GET", url, headers)
