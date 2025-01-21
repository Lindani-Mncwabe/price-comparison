import requests
import bs4

from src.obj import ItemSearchResult


def product_search(user_query: str, max_n_items: int) -> list[ItemSearchResult]:
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
