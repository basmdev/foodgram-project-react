from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    page_size = settings.PAGINATION
    page_size_query_param = "limit"
