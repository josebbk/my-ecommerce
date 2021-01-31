from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm
from store.models import Customer, OrderItem, Order, ShippingAddress
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginUserForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.views import login_required
from django.views.generic import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.utils import timezone


# TODO: send a code to email to confirm user
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # login after register
            # if you don't login after register, site won't be able to find the deleted cookie, and returns an error
            new_user = form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)

            device = request.COOKIES['device']
            customer, created = Customer.objects.get_or_create(device_code=device)
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')

            customer.name = first_name + ' ' + last_name
            customer.email = email
            customer.user = form.instance
            customer.phone_number = phone_number
            customer.save()

            # delete the current device cookie, then in base.html it creates a new one.
            response = HttpResponseRedirect('/')
            response.delete_cookie('device')

            messages.success(request, "Thanks for registering. You are now logged in.")
            return response
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form, 'title': 'Register'})


def login_page(request):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        if form.is_valid():

            # get info of user who is about to login
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            # login user
            if user is not None:
                login(request, user)
                messages.success(request, '{} Successfully Logged In.'.format(username))

                # get the guest user
                device = request.COOKIES['device']
                customer, created = Customer.objects.get_or_create(device_code=device, email=None)

                # get the user who logged in
                logged_in_customer = Customer.objects.get(user=request.user)
                logged_in_customer.device_code = device
                logged_in_customer.save()

                # get order items of the guest user, and turn them to order items of logged in user
                order_items = OrderItem.objects.filter(customer=customer, order_complete=False)
                logged_in_order_items = OrderItem.objects.filter(customer=logged_in_customer, order_complete=False)

                for i in order_items:
                    if i.item in [x.item for x in logged_in_order_items]:
                        lioi = logged_in_order_items.filter(item=i.item).first()
                        lioi.quantity += i.quantity
                        lioi.save()
                    else:
                        i.customer = logged_in_customer
                        i.save()

                # get order of guest and logged in user
                order = Order.objects.filter(customer=customer).first()
                logged_in_order, created = Order.objects.get_or_create(
                    customer=logged_in_customer,
                    order_complete=False,
                )

                # for loop on guest user items and give them to logged in user, and delete the guest user order
                if order is not None:
                    for o in order.items.all():
                        logged_in_order.items.add(o)
                        logged_in_order.save()
                    order.delete()

                # get rid of the used cookie
                response = HttpResponseRedirect('/')
                response.delete_cookie('device')

                # delete guest customer with device
                customer.delete()

                return response
            else:
                messages.warning(request, 'Your Username or Password Is Incorrect.')
    else:
        form = LoginUserForm()
    return render(request, 'users/login.html', {'form': form})


def logout_page(request):
    logout(request)
    return render(request, 'users/logout.html')


@login_required(login_url='login')
def profile(request):
    return render(request, 'users/profile.html')


@login_required(login_url='login')
def profile_edit(request):
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, instance=customer)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if p_form.is_valid() and u_form.is_valid():
            p_form.save()
            u_form.save()
            email = u_form.cleaned_data.get('email')
            first_name = u_form.cleaned_data.get('first_name')
            last_name = u_form.cleaned_data.get('last_name')
            customer.name = first_name + ' ' + last_name
            customer.email = email
            customer.user = request.user
            messages.success(request, f'Account Has Been Updated!!!')
            return redirect('profile-page')
    else:
        p_form = ProfileUpdateForm(instance=customer)
        u_form = UserUpdateForm(instance=request.user)
    context = {'p_form': p_form, 'u_form': u_form}
    return render(request, 'users/profile_info_edit.html', context)


@login_required(login_url='login')
def order_info(request):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.filter(customer=customer, order_complete=True).order_by('-ordered_date')
    context = {'order': order}
    return render(request, 'users/orders.html', context)


@login_required(login_url='login')
def order_detail(request, slug):
    customer = Customer.objects.get(user=request.user)
    order = get_object_or_404(Order, ref_code=slug, customer=customer)
    context = {'order': order}
    return render(request, 'users/order_detail.html', context)


@login_required(login_url='login')
def addresses(request):
    customer = Customer.objects.get(user=request.user)
    address = ShippingAddress.objects.filter(customer=customer).all()
    context = {"address": address}
    return render(request, 'users/addresses.html', context)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = ShippingAddress
    fields = ['name',
              'address',
              'country',
              'state_province',
              'city',
              'zip',
              'phone_number']
    template_name = 'users/address_form.html'

    def form_valid(self, form):
        customer = Customer.objects.get(user=self.request.user)
        form.instance.customer = customer
        return super().form_valid(form)

    def get_success_url(self):
        messages.info(self.request, 'Address Successfully Created.')
        return reverse('addresses-page')


class AddressUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ShippingAddress
    fields = ['name',
              'address',
              'country',
              'state_province',
              'city',
              'zip',
              'phone_number']
    template_name = 'users/address_form.html'

    def form_valid(self, form):
        customer = Customer.objects.get(user=self.request.user)
        form.instance.customer = customer
        return super().form_valid(form)

    def test_func(self):
        shipping_address = self.get_object()
        customer = Customer.objects.get(user=self.request.user)
        if customer == shipping_address.customer:
            return True
        return False

    def get_success_url(self):
        messages.info(self.request, 'Address Successfully Updated.')
        return reverse('addresses-page')


class AddressDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = ShippingAddress
    template_name = 'users/address_delete_confirm.html'

    # success_url = reverse_lazy('addresses-page')

    def test_func(self):
        shipping_address = self.get_object()
        customer = Customer.objects.get(user=self.request.user)
        if customer == shipping_address.customer:
            return True
        return False

    def get_success_url(self):
        messages.info(self.request, 'Address Successfully Deleted.')
        return reverse('addresses-page')
