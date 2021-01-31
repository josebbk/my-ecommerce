# to allow user to login not with only username, but using email too...
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            email = User.objects.get(email=username)
            if email.check_password(password) is True:
                return email
        except User.DoesNotExist:
            return None
