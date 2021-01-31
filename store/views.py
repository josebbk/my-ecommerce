from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.views.generic import DetailView, ListView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import *
from .utils import *
from django.contrib.auth.mixins import LoginRequiredMixin
from .filters import ProductFilter
from django_filters.views import FilterView


class HomeView(FilterView):
    # model = Product
    # for filtering products
    filterset_class = ProductFilter
    template_name = 'store/home.html'
    paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        product_filter = ProductFilter(self.request.GET, queryset=Product.objects.all())
        context.update({'myFilter': product_filter})
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product.html'


def add_to_cart(request, slug):
    # function from utils.py
    customer = get_customer(request)

    product = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        customer=customer,
        item=product,
        order_complete=False,
    )
    order_qs = Order.objects.filter(customer=customer, order_complete=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in order
        if order.items.filter(item__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, 'Your Quantity Was Updated.')
            return redirect('cart-page')
        else:
            order.items.add(order_item)
            messages.success(request, "This Item Was Added To Your Cart.")
            return redirect('cart-page')
    else:
        time = timezone.now()
        order = Order.objects.create(
            customer=customer,
            ordered_date=time,
        )
        order.items.add(order_item)
        messages.info(request, "This Item Was Added To Your Cart.")
        return redirect('cart-page')


def remove_from_cart(request, slug):
    # function from utils.py
    customer = get_customer(request)

    product = get_object_or_404(Product, slug=slug)
    order_item = OrderItem.objects.filter(customer=customer, order_complete=False, item=product)

    if order_item.exists():
        # delete item from OrderItem
        order_item.delete()
        messages.info(request, "This Item Was Removed From Your Cart.")
        return redirect('cart-page')
    else:
        messages.info(request, "This Item Was Not In Your Cart.")
        return redirect('product-page', slug=slug)


def remove_single_item_from_cart(request, slug):
    # function from utils.py
    customer = get_customer(request)

    product = Product.objects.get(slug=slug)
    order_item = OrderItem.objects.get(customer=customer, order_complete=False, item=product)
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
        messages.success(request, "Your Quantity Was Updated.")
    else:
        order_item.delete()
        messages.info(request, "This Item Was Removed From Your Cart.")
    return redirect('cart-page')


class CartView(View):
    def get(self, *args, **kwargs):
        customer = get_customer(self.request)
        try:
            order, created = Order.objects.get_or_create(customer=customer, order_complete=False)
            context = {'order': order, 'couponform': CouponForm, 'DISPLAY_COUPON_FORM': True}
            return render(self.request, 'store/cart.html', context)
        except:
            messages.warning(self.request, "You Cart Is Empty.")
            return redirect('home-page')


class CheckOutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        # function from utils.py
        customer = get_customer(self.request)
        # for __init_ in form.py need to pass the current customer
        form = CheckOutForm(customer)

        if ShippingAddress.objects.filter(customer=customer).all().exists():
            address_exists = True
        else:
            address_exists = False

        try:
            order = Order.objects.get(customer=customer, order_complete=False)
            if order.items.count() >= 1:
                context = {
                    'order': order,
                    'form': form,
                    'couponform': CouponForm,
                    'DISPLAY_COUPON_FORM': False,
                    'address_exists': address_exists
                }

                return render(self.request, 'store/checkout.html', context)
            else:
                messages.warning(self.request, "You Cart Is Empty.")
                return redirect('cart-page')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You Don't Have An Active Cart.")
            return redirect('home-page')

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            customer = get_customer(self.request)
            form = CheckOutForm(customer, self.request.POST)
            if form.is_valid():

                # function from utils.py
                customer = get_customer(self.request)

                order = Order.objects.get(customer=customer, order_complete=False)
                address = form.cleaned_data.get('address')
                order.shipping_address = address
                order.save()

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'S':
                    return redirect('payment-page', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('payment-page', payment_option='paypal')
                elif payment_option == 'T':
                    return redirect('payment-page', payment_option='test-user')
            else:
                messages.warning(self.request, "Please Create An Address.")
                return redirect('checkout-page')

    # to show message if guest user goes to checkout page
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "Please Create An Account To Proceed, Or Login.")
            return self.handle_no_permission()
        return super().dispatch(self.request, *args, **kwargs)


class AddCouponView(View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = CouponForm(self.request.POST)

            if form.is_valid():
                # from utils.py
                customer = get_customer(self.request)
                code = form.cleaned_data.get('code')
                order = Order.objects.get(customer=customer, order_complete=False)
                # from utils.py
                coupon = get_coupon(self.request, code)
                order.coupon = coupon
                if order.coupon is None:
                    messages.warning(self.request, "This Coupon Code Does Not Exist.")
                    return redirect('cart-page')
                else:
                    # save and overwrite old code if exists
                    order.save()
                    messages.success(self.request, "Coupon Code Added.")
                    return redirect('cart-page')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # ORDER
        customer = get_customer(self.request)
        try:
            order = Order.objects.get(customer=customer, order_complete=False)
            if order.shipping_address:
                context = {
                    'order': order,
                    'DISPLAY_COUPON_FORM': False
                }
                return render(self.request, 'store/payment.html', context)
            else:
                messages.warning(self.request, 'Fill Out The Checkout Form')
                return redirect('checkout-page')
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You Have No Active Order')
            return redirect('home-page')

    def post(self, *args, **kwargs):
        customer = get_customer(self.request)

        order = Order.objects.get(customer=customer, order_complete=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        # from utils.py
        p = payment_charge_post(self.request, customer, order, token, amount)
        # if error stripe occurred
        if p == 'error':
            return redirect('payment-page')
        else:
            return redirect('home-page')

    # to show message if guest user goes to checkout page
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "Please Create An Account To Proceed, Or Login.")
            return self.handle_no_permission()
        return super().dispatch(self.request, *args, **kwargs)


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        context = {
            'form': RefundForm
        }
        return render(self.request, 'store/request_refund.html', context)

    def post(self, *args, **kwargs):

        if self.request.method == 'POST':
            form = RefundForm(self.request.POST)

            if form.is_valid():
                ref_code = form.cleaned_data.get('ref_code')
                name = form.cleaned_data.get('name')
                reason = form.cleaned_data.get('reason')
                phone_number = form.cleaned_data.get('phone_number')

                try:
                    # edit order
                    order = Order.objects.get(ref_code=ref_code, order_complete=True, refund_requested=False)
                    order.refund_requested = True
                    order.save()
                    # create refund request
                    refund = Refund(order=order, name=name, reason=reason, phone_number=phone_number)
                    refund.save()
                    messages.info(self.request, 'Your Request Has Been Sent. We Will Contact You.')
                    return redirect('refund-page')

                except ObjectDoesNotExist:
                    messages.info(self.request,
                                  'There Is No Such Order In Our DataBase. Or You May Have Already Requested A Refund')
                    return redirect('refund-page')

            else:
                messages.warning(self.request, 'Invalid Input.')
                return redirect('refund-page')
