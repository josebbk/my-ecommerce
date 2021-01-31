# shows cart quantity

from django import template
from store.models import Order, Customer

register = template.Library()


@register.filter
def cart_item_count(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        qs = Order.objects.filter(customer=customer, order_complete=False)
        if qs.exists():
            return qs[0].items.count()
        else:
            return 0
    else:
        try:
            device = request.COOKIES['device']
            customer = Customer.objects.get(device_code=device)
            qs = Order.objects.filter(customer=customer, order_complete=False)
            if qs.exists():
                return qs[0].items.count()
            else:
                return 0
        except KeyError:
            return 0
