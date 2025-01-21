from typing import Annotated, Final
import pydantic
import requests
import bs4
import urllib.parse
import argparse
import json

# obj.py
def is_non_negative(value: int) -> int:
    """Validates that input integer is non-negative.
    Used for pydantic field validation
    """
    if value < 0:
        raise ValueError(f"{value:,} is negative")
    return value


class ItemSearchResult(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    item_title: str
    item_image_url: str
    price_cents: Annotated[int, pydantic.AfterValidator(is_non_negative)]



# Checkers.py search
def checkers_product_search(user_query: str, max_n_items: int) -> list[ItemSearchResult]:
    """
    TODO
    """

    response = requests.get(
        "https://www.checkers.co.za/search/all",
        params={
            "q": user_query,
        },
        # cookies=cookies,
        headers={
            "accept-language": "en-US,en;q=0.9",
            "priority": "u=0, i",
            "referer": "https://www.checkers.co.za/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        },
    )
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    item_products = soup.find_all(class_="item-product")
    if len(item_products) > max_n_items:
        item_products = item_products[:max_n_items]
    return [
        ItemSearchResult(
            item_title=item.find(class_="product-listening-click").get("title").strip(),
            item_image_url=f'https://www.checkers.co.za{item.find(class_="item-product__image __image").find("img").get("data-original-src")}',
            price_cents=int(
                item.find(class_="js-item-product-price")
                .find(class_="now")
                .text.replace("R", "")
                .replace(".", "")
                .strip()
            ),
        )
        for item in item_products
    ]


# PnP.py search
def pnp_product_search(user_query: str, max_n_items: int) -> list[ItemSearchResult]:
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

# woolworths.py search
def woolworths_product_search(user_query: str, max_n_items: int) -> list[ItemSearchResult]:
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


# cli_product_search.py
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("vendor_name", type=str)
    arg_parser.add_argument("search_query", type=str)
    arg_parser.add_argument("max_n_results", type=int)
    args = arg_parser.parse_args()
    match args.vendor_name:
        case "checkers":
            prod_search = checkers_product_search
        case "picknpay":
            prod_search = pnp_product_search
        case "woolworths":
            prod_search = woolworths_product_search
        case _:
            raise ValueError(f"vendor '{args.vendor_name}' is not recognised.")
    search_results: list[ItemSearchResult] = prod_search(
        user_query=args.search_query,
        max_n_items=args.max_n_results,
    )
    print(
        json.dumps(
            [item.model_dump() for item in search_results],
            indent=4,
        )
    )
