from django.core.paginator import Paginator

from posts.constant import M_CONSTANT


def paginator(n_list, request):
    paginator = Paginator(n_list, M_CONSTANT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
