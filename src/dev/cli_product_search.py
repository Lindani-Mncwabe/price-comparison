import argparse
import json

from src.obj import ItemSearchResult
from src.vendor import checkers, picknpay, woolworths

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("vendor_name", type=str)
    arg_parser.add_argument("search_query", type=str)
    arg_parser.add_argument("max_n_results", type=int)
    args = arg_parser.parse_args()
    match args.vendor_name:
        case "checkers":
            prod_search = checkers.product_search
        case "picknpay":
            prod_search = picknpay.product_search
        case "woolworths":
            prod_search = woolworths.product_search
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
