
# shows cart quantity

# from django import template
# from store.models import Order
# from store.utils import get_customer
#
# register = template.Library()
#
#
# @register.filter
# def cart_item_count(request):
#     customer = get_customer(request)
#     qs = Order.objects.filter(customer=customer, order_complete=False)
#     if qs.exists():
#         return qs[0].items.count()
#     return 0
# <span class="badge red z-depth-1 mr-1"> {{ request|cart_item_count }} </span>