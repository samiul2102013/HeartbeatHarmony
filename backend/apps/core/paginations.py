from rest_framework.pagination import PageNumberPagination


class LimitOffsetPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {'type': 'integer'},
                'next': {'type': 'string', 'nullable': True},
                'previous': {'type': 'string', 'nullable': True},
                'results': schema,
            },
        }