from django.urls import path
from users import views as users_views

urlpatterns = [
    path('register/', users_views.register, name='register'),
    path('login/', users_views.login_page, name='login'),
    path('logout/', users_views.logout_page, name='logout'),
    path('profile/', users_views.profile, name='profile-page'),
    path('profile/edit', users_views.profile_edit, name='profile-edit-page'),
    path('profile/orders', users_views.order_info, name='orders-page'),
    path('profile/order-detail/<slug>/', users_views.order_detail, name='order-detail-page'),
    path('profile/addresses', users_views.addresses, name='addresses-page'),
    path('profile/address-update/<int:pk>/', users_views.AddressUpdateView.as_view(), name='address-update-page'),
    path('profile/address-create/', users_views.AddressCreateView.as_view(), name='address-create-page'),
    path('profile/address-delete/<int:pk>/', users_views.AddressDeleteView.as_view(), name='address-delete-page'),
]