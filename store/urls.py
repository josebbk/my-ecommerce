from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home-page'),
    path('checkout/', CheckOutView.as_view(), name='checkout-page'),
    path('product/<slug>/', ProductDetailView.as_view(), name='product-page'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('cart/', CartView.as_view(), name='cart-page'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment-page'),
    path('request-refund/', RequestRefundView.as_view(), name='refund-page'),
    path('add-coupon/', AddCouponView.as_view(), name='coupon-page'),
]
