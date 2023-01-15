from django.core.paginator import Paginator
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet

NUMBERS_PAGES = 10


def get_page(queryset: QuerySet, request: WSGIRequest) -> dict:
    """Функция для разбиения записей из базы данных
    постранично.
    """
    paginator = Paginator(queryset, NUMBERS_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }
