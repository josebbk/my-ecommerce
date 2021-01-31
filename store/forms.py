from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.core.validators import RegexValidator
from .models import *

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
    ('T', 'UserTest')
)


class CheckOutForm(forms.Form):
    address = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=None)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

    # filter address by current user
    def __init__(self, user, *args, **kwargs):
        super(CheckOutForm, self).__init__(*args, **kwargs)
        self.fields['address'].queryset = ShippingAddress.objects.filter(customer=user)


class CouponForm(forms.Form):
    code = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': "Recipient's username",
        'aria-describedby': 'basic-addon2',
    }))


phone_regex = RegexValidator(
    regex=r'(0|\+98)?([ ]|-|[()]){0,2}9[0|1|2|3|4]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}',
    message="Insert A Valid Phone Number Like: 0911*****21.")


class RefundForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Full Name'
    }))
    ref_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Reference Code'
    }))
    reason = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': ' Reason For Refund'
    }))
    phone_number = forms.CharField(validators=[phone_regex], max_length=11, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
