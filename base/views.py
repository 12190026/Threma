from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .models import  ExecutiveMember, Practitioner, Activity, FinancialStatement
from .forms import ExecutiveMemberForm, PractitionerForm, LoginForm, ActivityForm, FinancialStatementForm, CidForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .backends import CustomBackend
from django.utils import timezone


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
            messages.error(request, 'Invalid login credentials.')
            return render(request, 'base/adminlogin.html')  # Update this response as needed
    context = {'page': page}
    return render(request, 'base/adminlogin.html', context)  





# def login_executive(request):
#     page = 'executivelogin'

#     if request.method == 'POST':
#         cid = request.POST.get('cid')
#         password = request.POST.get('password')
#         user = authenticate(request, cid=cid, password=password, backend='base.backends.CustomBackend')
#         if user is not None:
#             login(request, user)
#             return redirect('index')
#         else:
#             messages.error(request, 'Invalid login credentials.')
#     context = {'page': page}
#     return render(request, 'base/executivelogin.html', context)

def login_executive(request):
    page = 'executivelogin'

    # Get all unique roles from the database
    roles = set(ExecutiveMember.objects.values_list('role', flat=True))

    if request.method == 'POST':
        cid = request.POST.get('cid')
        password = request.POST.get('password')
        role = request.POST.get('role')
        user = authenticate(request, cid=cid, password=password, role=role, backend='base.backends.CustomBackend')
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid login credentials.')
    context = {'page': page, 'roles': roles}
    return render(request, 'base/executivelogin.html', context)

def main(request):
    user = request.user  # Get the authenticated user
    executive_member = ExecutiveMember.objects.get(cid=user.cid)  # Retrieve the ExecutiveMember object

    context = {
        'name': executive_member.name,  # Pass the name to the template context
    }
    
    return render(request, 'main.html', context)


@login_required(login_url=('adminlogin', 'executivelogin'))
def index(request):
    # Retrieve the counts from the database
    total_members = ExecutiveMember.objects.count()
    total_practitioners = Practitioner.objects.count()
    total_activities = Activity.objects.count()

    # Pass the counts to the template
    context = {
        'total_members': total_members,
        'total_practitioners': total_practitioners,
        'total_activities': total_activities
    }
    return render(request, 'base/index.html', context)

@login_required(login_url=('adminlogin', 'executivelogin'))
def transferform(request):
     return render(request, 'base/transferform.html')


@login_required(login_url=('adminlogin', 'executivelogin'))
def finance(request):
    finance = FinancialStatement.objects.all().values()
    context = {
        'FinancialStatement': finance
    }
    
    return render(request, 'base/finance.html', context)

@login_required(login_url=('adminlogin', 'executivelogin'))
def activity(request):
    activity = Activity.objects.all().values()
    context = {
        'Activity': activity
    }
    
    return render(request, 'base/activity.html', context)

@login_required(login_url=('adminlogin', 'executivelogin'))
def profile(request):
    user = request.user  # Get the authenticated user
    executive_member = ExecutiveMember.objects.get(cid=user.cid)  # Retrieve the ExecutiveMember object

    context = {
        'name': executive_member.name, 
        'present_address': executive_member.present_address, 
        'village': executive_member.village,
        'geog': executive_member.geog,
        'dzongkhag': executive_member.dzongkhag,   
        'cid': executive_member.cid,
        'email': executive_member.email, 
        'contact_no': executive_member.contact_no, 
        'responsibility': executive_member.responsibility,   # Pass the name to the template context
    }

    return render(request, 'base/profile.html', context)

def update_activity_status(request, activity_id):
    activity = Activity.objects.get(activity_id=activity_id)
    if request.method == 'POST':
        activity.status = 'COMPLETED'  # replace with your desired logic
        activity.save()
    return redirect('activity')



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

def search_executive_member(request):
    query = request.GET.get('q')
    if query:
        results = ExecutiveMember.objects.filter(name__icontains=query)
    else:
        results = None
    context = {'results': results}
    return render(request, 'base/executives.html', context)


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

@login_required
def add_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity has been added successfully!')
            return redirect('activity')
        else:
            messages.error(request, 'Error occurred while adding activity. Please try again.')
    else:
        form = ActivityForm()
    return render(request, 'base/activity.html', {'form': form})


def upload_statement(request):
    if request.method == 'POST':
        form = FinancialStatementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('finance')
        else:
            messages.error(request, 'Error occurred while adding Financial Statement. Please try again.')
    else:
        form = FinancialStatementForm()
    year_choices = [year for year in range(2015, 2031)]
    context = {'form': form, 'year_choices': year_choices}
    return render(request, 'base/finance.html', context)


def display_member_info(request):
    if request.method == 'POST':
        form = CidForm(request.POST)
        if form.is_valid():
            cid = form.cleaned_data['cid']
            member = ExecutiveMember.objects.get(cid=cid)
            context = {
                    'name': member.name, 
                    'cid': member.cid,
                    'email': member.email, 
                    'contact_no': member.contact_no, 
                'responsibility': member.responsibility,   # Pass the name to the template context
                }
            print(member)
            return render(request, 'base/transferform.html', {'form': form, 'member': member})
        else:
            messages.error(request, 'Error occurred while adding Financial Statement. Please try again.')
    else:
        form = CidForm()
    
    return render(request, 'base/transferform.html', {'form': form}, context)


# UI Starts from here on out

def home(request):
    return render(request, 'ui/home.html')

    
def aboutus(request):
    return render(request, 'ui/aboutus.html')