from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page-size'
    max_page_size = 100

    def build_response_data(self, data):
        return {
            'total_count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_size': self.page.paginator.per_page,
            'results': data,
        }

    def get_paginated_response(self, data):
        return Response(self.build_response_data(data))
