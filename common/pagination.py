from math import ceil
from common.exceptions import ValidationError


def paginate_queryset(qs, *, page: int, page_size: int):
    if page < 1:
        raise ValidationError("page must be >= 1")
    if page_size < 1 or page_size > 50:
        raise ValidationError("page_size must be between 1 and 50")

    total = qs.count()
    offset = (page - 1) * page_size
    items = list(qs[offset : offset + page_size])

    total_pages = ceil(total / page_size) if page_size else 1
    return {
        "count": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "results": items,
    }
