from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import MultipleObjectsReturned
from .models import ExecutiveMember

class CustomBackend(BaseBackend):
    def authenticate(self, request, cid=None, password=None, **kwargs):
        try:
            user = ExecutiveMember.objects.get(cid=cid, password=password)
        except ExecutiveMember.DoesNotExist:
            return None

        if user.role:
            return user

    def get_user(self, user_id):
        try:
            return ExecutiveMember.objects.get(pk=user_id)
        except ExecutiveMember.DoesNotExist:
            return None
