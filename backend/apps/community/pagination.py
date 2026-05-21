from rest_framework.pagination import PageNumberPagination


class CommunityPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_page_size(self, request):
        for param in (self.page_size_query_param, 'per_page', 'page_size'):
            if not param:
                continue
            raw = request.query_params.get(param)
            if raw is not None:
                try:
                    size = int(raw)
                    if size > 0:
                        return min(size, self.max_page_size)
                except (TypeError, ValueError):
                    pass
        return self.page_size
