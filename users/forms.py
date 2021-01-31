from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import TextInput, PasswordInput
from django.core.validators import RegexValidator
from store.models import Customer

phone_regex = RegexValidator(
    regex=r'(0|\+98)?([ ]|-|[()]){0,2}9[0|1|2|3|4]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}',
    message="Insert A Valid Phone Number Like: 0911*****21.")


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True)
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Username'}),
                               required=True)
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'First Name (optional)'}),
                                 required=False)
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Last Name (optional)'}),
                                required=False)
    password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
                                required=True)
    password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
                                required=True)
    phone_number = forms.CharField(validators=[phone_regex], max_length=11, required=True,
                                   widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']


class LoginUserForm(forms.Form):
    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Username/Email'}),
                               label=False)
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}),
                               label=False)


class ProfileUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(validators=[phone_regex], max_length=11, required=True)

    class Meta:
        model = Customer
        fields = ['phone_number']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
