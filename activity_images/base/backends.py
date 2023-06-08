from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import MultipleObjectsReturned
from .models import ExecutiveMember
from django.contrib.auth.hashers import make_password

class CustomBackend(BaseBackend):
    def authenticate(self, request, cid=None, password=None, role=None, **kwargs):
        try:
            user = ExecutiveMember.objects.get(cid=cid, password=password, role=role)
        except ExecutiveMember.DoesNotExist:
            return None

        return user

    def get_user(self, user_id):
        try:
            return ExecutiveMember.objects.get(pk=user_id)
        except ExecutiveMember.DoesNotExist:
            return None

    def change_password(self, user, new_password):
        hashed_password = make_password(new_password)
        user.password = hashed_password
        user.save()