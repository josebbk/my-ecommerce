from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.utils import timezone

phone_regex = RegexValidator(
    regex=r'(0|\+98)?([ ]|-|[()]){0,2}9[0|1|2|3|4]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}',
    message="Insert A Valid Phone Number Like: 0911*****21.")

CATEGORY_CHOICES = (
    ("S", "Shirt"),
    ("SW", "Sport wear"),
    ("OW", "Outwear"),
)

LABEL_CHOICES = (
    ("P", "primary"),
    ("S", "secondary"),
    ("D", "danger"),
)

ATTRIBUTE_CHOICES = (
    ('N', 'NEW'),
    ('BS', 'BestSeller'),
    ('PP', 'Popular')
)

STATUS_CHOICES = (
    ('PC', 'Processing'),
    ('BD', 'Being Delivered'),
    ('R', 'Received'),
)


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=11, blank=True)  # validators should be a list
    device_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        if self.user:
            return str(self.user)
        elif self.device_code:
            return str(self.device_code)


class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(default='default.jpg', upload_to='product_images')
    description = models.TextField(default='There Is No Description')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, blank=True)
    attribute = models.CharField(choices=ATTRIBUTE_CHOICES, max_length=2, blank=True)
    slug = models.SlugField(null=True, blank=True, unique=True)

    def __str__(self):
        if self.discount_price:
            return "{} | {}".format(self.title, self.discount_price)
        else:
            return "{} | {}".format(self.title, self.price)

    def get_absolute_url(self):
        return reverse('product-page', kwargs={
            'slug': self.slug
        })

    def get_add_to_cart(self):
        return reverse('add-to-cart', kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart(self):
        return reverse('remove-from-cart', kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    order_complete = models.BooleanField(default=False)

    def __str__(self):
        return "{} | {} | Complete: {}".format(self.customer, self.item.title, self.order_complete)

    def get_total_price(self):
        return self.item.price * self.quantity

    def get_total_discount_price(self):
        return self.item.discount_price * self.quantity

    def amount_saved(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.item.discount_price != 0:
            return self.get_total_discount_price()
        else:
            return self.get_total_price()


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone_number = models.CharField(validators=[phone_regex], max_length=11)
    country = CountryField(multiple=False)
    state_province = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    address = models.TextField()
    zip = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return "{} | {} | {}".format(self.customer, self.country, self.address)

    def get_absolute_url(self):
        return reverse('addresses-page')


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} | {}".format(self.customer, self.amount)


class Coupon(models.Model):
    code = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    used = models.BooleanField(default=False)

    def __str__(self):
        return "{} | {}".format(self.code, self.amount)


class Order(models.Model):
    ref_code = models.CharField(max_length=25, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField(default=timezone.now)
    order_complete = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, blank=True, default=STATUS_CHOICES[0][0])
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return "{} | {}".format(self.customer, self.ordered_date)

    def get_total(self):
        total = 0
        for item in self.items.all():
            total += item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_absolute_url(self):
        return reverse('order-detail-page', kwargs={
            'slug': self.ref_code
        })


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    phone_number = models.CharField(validators=[phone_regex], max_length=11)
    ref_code = models.CharField(blank=True, null=True, max_length=12)
    refund_requested_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} | {} | Accepted: {}".format(self.name, self.phone_number, self.accepted)
