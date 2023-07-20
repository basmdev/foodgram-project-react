from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class CustomPaginator(PageNumberPagination):
    page_size = settings.PAGINATION
    page_size_query_param = "limit"
