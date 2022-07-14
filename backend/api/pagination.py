from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    limit = 9
    page_size_query_param = 'limit'