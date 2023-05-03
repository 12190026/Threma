from django.utils import timezone
from django.contrib.auth import authenticate
from django.shortcuts import redirect

def custom_login(request, cid, password):
    executive_member = authenticate(request, cid=cid, password=password)
    if executive_member is not None:
        login(request, executive_member)
        executive_member.last_login = timezone.now()
        executive_member.save()
        return redirect('index')
    else:
        messages.error(request, 'Invalid credentials')
        return redirect('executivelogin')
