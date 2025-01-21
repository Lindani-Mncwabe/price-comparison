import requests

from src.obj import ItemSearchResult


def product_search(user_query: str, max_n_items: int) -> list[ItemSearchResult]:
    """
    TODO
    """

    response = requests.post(
        url="https://www.pnp.co.za/pnphybris/v2/pnp-spa/products/search",
        params={
            "query": user_query,
            "pageSize": max_n_items,
            "storeCode": "WC44",
            "lang": "en",
            "curr": "ZAR",
        },
        headers={
            "Content-Type": "application/json",
            "origin": "https://www.pnp.co.za",
            "referer": f"https://www.pnp.co.za/search/{requests.utils.quote(user_query)}",
            "User-Agent": "Please let me in",
        },
    )

    items_info_raw: dict = response.json()["products"]
    if len(items_info_raw) > max_n_items:
        items_info_raw = items_info_raw[:max_n_items]
    return [
        ItemSearchResult(
            item_title=item["name"],
            item_image_url=[
                image["url"]
                for image in item["images"]
                if image["format"] == "product" and image["imageType"] == "PRIMARY"
            ][0],
            price_cents=int(100 * item["price"]["value"]),
        )
        for item in items_info_raw
    ]
