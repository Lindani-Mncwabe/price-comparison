import requests
import urllib.parse
from typing import Final

from src.obj import ItemSearchResult


def product_search(user_query: str, max_n_items: int) -> list[ItemSearchResult]:
    """
    Search for a product on www.woolworths.co.za
    """
    req_params: dict = {
        "Accept": "application/json",
        "pageURL": "/cat",
        "Ntt": user_query,
        "Dy": 1,
    }
    req_headers: dict = {
        "User-Agent": "Please let me in",
        "Referer": "https://www.woolworths.co.za/cat",
        "X-requested-by": "Woolworths Online",
    }
    response = requests.get(
        url="https://www.woolworths.co.za/server/searchCategory",
        params=req_params,
        headers=req_headers,
    )
    MAX_N_REDIRECTS: Final[int] = 10
    for _ in range(MAX_N_REDIRECTS):
        response_json: dict = response.json()
        response_content: dict
        if isinstance(response_json["contents"], list):
            response_content = response_json["contents"][0]
        else:
            response_content = response_json["contents"]
        if response_content["@type"] == "Redirect":
            redirect_url: str = response_content["redirectURL"]
            parsed_redirect_url = urllib.parse.urlparse(redirect_url)
            response = requests.get(
                url=f"https://www.woolworths.co.za/server/searchCategory",
                params={"pageURL": parsed_redirect_url.path},
                headers=req_headers,
            )
        else:
            break
    items_info_raw: list[dict] = response_content["mainContent"][0]["contents"][0][
        "records"
    ]
    if len(items_info_raw) > max_n_items:
        items_info_raw = items_info_raw[:max_n_items]

    items_info: list[dict] = [
        {
            "item_title": item["attributes"]["p_displayName"],
            "item_image_url": item["attributes"]["p_externalImageReference"],
            "item_prices": item["startingPrice"],
        }
        for item in items_info_raw
    ]
    return [
        ItemSearchResult(
            item_title=item.get("item_title"),
            item_image_url=item.get("item_image_url"),
            price_cents=int(100 * item["item_prices"].get("p_pl00")),
        )
        for item in items_info
    ]
