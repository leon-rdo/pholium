from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that allows clients to set the page size
    using a 'limit' query parameter. The maximum page size is capped at 100,
    and the default page size is set to 20.
    """

    page_size_query_param = "limit"
    max_page_size = 100
    page_size = 20
