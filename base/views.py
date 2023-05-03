from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .models import  ExecutiveMember, Practitioner
from .forms import ExecutiveMemberForm, PractitionerForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .backends import CustomBackend


def login_admin(request):
    page = 'adminlogin'

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return render(request, 'base/index.html')  # Update this response as needed
        else:
            return render(request, 'base/adminlogin.html')  # Update this response as needed
    context = {'page': page}
    return render(request, 'base/adminlogin.html', context)  



def login_executive(request):
    if request.method == 'POST':
        cid = request.POST.get('cid')
        password = request.POST.get('password')
        user = authenticate(request, cid=cid, password=password, backend='base.backends.CustomBackend')
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid login credentials.')
    return render(request, 'base/executivelogin.html')


def index(request):
    return render(request, 'base/index.html')

def executives(request):
    member = ExecutiveMember.objects.all().values()
    context = {
        'ExecutiveMember': member
    }

    return render(request, 'base/executives.html', context)

def practitioner(request):
    member = Practitioner.objects.all().values()
    context = {
        'Practitioner': member
    }

    return render(request, 'base/practitioner.html', context)


def add_member(request):
    if request.method == 'POST':
        form = ExecutiveMemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member added successfully.')  # Show success message
            return redirect('executives')
        else:
            messages.error(request, 'Form submission failed. Please check your input.')  # Show error message
    return render(request, 'base/executives.html', {'form': form})

def add_member_practitioner(request):
    if request.method == 'POST':
        form = PractitionerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Practitioner added successfully.')  # Show success message
            return redirect('practitioner')
        else:
            messages.error(request, 'Form submission failed. Please check your input.')  # Show error message
    return render(request, 'base/practitioner.html', {'form': form})


# UI Starts from here on out

def home(request):
    return render(request, 'ui/home.html')