from typing import Final

import fastapi
import fastapi.responses
import fastapi.staticfiles

from src.vendor import checkers, picknpay, woolworths

app = fastapi.FastAPI()

app.mount(
    "/static",
    fastapi.staticfiles.StaticFiles(directory="static"),
    name="static",
)


@app.get("/", response_class=fastapi.responses.HTMLResponse)
def index():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        html: str = file.read()
    return fastapi.responses.HTMLResponse(content=html)


@app.get("/product-search")
def product_search(
    query: str = fastapi.Query(None, description="Product search keywords")
):
    MAX_N_ITEMS: Final[int] = 5
    search_results: dict = {
        "checkers": [
            x.model_dump()
            for x in checkers.product_search(
                user_query=query,
                max_n_items=MAX_N_ITEMS,
            )
        ],
        "picknpay": [
            x.model_dump()
            for x in picknpay.product_search(
                user_query=query,
                max_n_items=MAX_N_ITEMS,
            )
        ],
        "woolworths": [
            x.model_dump()
            for x in woolworths.product_search(
                user_query=query,
                max_n_items=MAX_N_ITEMS,
            )
        ],
    }
    return search_results
