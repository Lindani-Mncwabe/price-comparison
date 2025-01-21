from typing import Annotated

import pydantic


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
