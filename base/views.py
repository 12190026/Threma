from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import  ExecutiveMember, Practitioner, Activity, FinancialStatement, Semso, Transfer
from .forms import ExecutiveMemberForm, PractitionerForm, LoginForm, TransferForm, ActivityForm, FinancialStatementForm, CidForm, ProfilePictureForm, PasswordChangeForm, SemsoForm, BulkUploadForm, ChangePasswordForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .backends import CustomBackend
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.db.models import Count
import matplotlib.pyplot as plt
from django.views.generic import View
import os
from django.conf import settings
import json
import pandas as pd



def login_admin(request):
    page = 'adminlogin'

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('index')  # Update this response as needed
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
            # Check if the input role matches the user's role
            if user.role == role:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid role for the user.')
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


@login_required(login_url='adminlogin')
def index(request):
    # Retrieve the counts from the database
    total_members = ExecutiveMember.objects.count()
    total_practitioners = Practitioner.objects.count()
    total_activities = Activity.objects.count()

    # Retrieve the counts for each stage of threma
    stage_counts = Practitioner.objects.values('stage_of_threma').annotate(count=Count('stage_of_threma'))

    # Extract the stage labels and count values
    labels = [stage['stage_of_threma'] for stage in stage_counts]
    counts = [stage['count'] for stage in stage_counts]

    # Pass the labels and counts to the template context as JSON strings
    labels_json = json.dumps(labels)
    counts_json = json.dumps(counts)

    # Pass the data to the template context
    context = {
        'total_members': total_members,
        'total_practitioners': total_practitioners,
        'total_activities': total_activities,
        'labels': labels_json,
        'counts': counts_json,
    }

    return render(request, 'base/index.html', context)

def transferform(request):
    if request.method == 'POST':
        form = TransferForm(request.POST, request.FILES)
        if form.is_valid():
            cid = form.cleaned_data['cid']
            reason = form.cleaned_data['reason']
            picture = form.cleaned_data['picture']
            practitioner = Practitioner.objects.get(cid=cid)
            transfer = Transfer(practitioner=practitioner, reason=reason, picture=picture)
            transfer.save()
            return redirect('transferform')  # Redirect to the transferform view after successful submission
    else:
        form = TransferForm()

    transfers = Transfer.objects.all()  # Retrieve all transfer objects from the database
    practitioner = Practitioner.objects.last()  # Retrieve the latest practitioner object from the database
    context = {
        'form': form,
        'transfers': transfers,
        'practitioner': practitioner  # Pass the practitioner object to the template context
    }

    return render(request, 'base/transferform.html', context)


from .forms import PictureUploadForm

def upload_image(request):
    if request.method == 'POST':
        cid = request.POST.get('cid')
        image = request.FILES.get('image')

        try:
            transfer = Transfer.objects.get(practitioner__cid=cid)
            transfer.picture = image
            transfer.save()

            # Return a JSON response to indicate a successful upload
            return JsonResponse({'message': 'Image uploaded successfully'})
        
        except Transfer.DoesNotExist:
            # Return a JSON response with an error message if the Transfer object does not exist
            return JsonResponse({'error': 'Transfer does not exist'})

    # Return a JSON response with an error message if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'})



def upload_picture(request, cid):
    if request.method == 'POST':
        # Assuming you have a model named Transfer to store the picture
        # Retrieve the transfer based on the given cid
        try:
            transfer = Transfer.objects.get(practitioner__cid=cid)
        except Transfer.DoesNotExist:
            return JsonResponse({'message': 'Transfer not found'}, status=404)
        
        # Retrieve the uploaded picture from the request
        picture = request.FILES.get('picture')
        
        if picture:
            # Save the picture to the transfer
            transfer.picture = picture
            transfer.save()
            
            return JsonResponse({'message': 'Picture uploaded successfully'})
        else:
            return JsonResponse({'message': 'No picture found in the request'}, status=400)
    
    return JsonResponse({'message': 'Invalid request method'}, status=405)

def get_letter(request):
    cid = request.GET.get('cid')

    transfers = Transfer.objects.filter(practitioner__cid=cid)

    practitioners = []
    for transfer in transfers:
        practitioners.append(transfer.practitioner)

    context = {
        'practitioners': practitioners,
    }

    return render(request, 'base/transferform.html', context)

def view_letter(request, transfer_id):
    transfer = get_object_or_404(Transfer, pk=transfer_id)
    practitioner = transfer.practitioner

    return render(request, 'base/transferform.html', {'practitioner': practitioner})

def retrieve_practitioner(request):
    cid = request.GET.get('cid')
    try:
        transfer = Transfer.objects.select_related('practitioner').get(practitioner__cid=cid)
        practitioner = transfer.practitioner

        data = {
            'name': practitioner.name,
            'cid': practitioner.cid,
            'contact_no': practitioner.contact_no,
            'dzongkhag': practitioner.dzongkhag,
            'gewog': practitioner.geog,
            'village': practitioner.village,
            'reason': transfer.reason,
            'date': transfer.date.isoformat(),
        }

        if transfer.picture:
            data['picture'] = transfer.picture.url

        return JsonResponse(data)
    except Transfer.DoesNotExist:
        return JsonResponse({'error': 'Practitioner not found'})

def change_status(request, cid):
    transfer = get_object_or_404(Transfer, practitioner__cid=cid)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            transfer.status = 'approved'
            transfer.save()

        elif action == 'reject':
            transfer.status = 'rejected'
            transfer.save()

        return redirect('transferform')

    context = {
        'transfer': transfer,
        'cid': cid,  # Add the cid value to the context
    }
    return render(request, 'base/transferform.html', context)


@login_required(login_url=('adminlogin', 'executivelogin'))
def finance(request):
    finance = FinancialStatement.objects.all()
    context = {
        'FinancialStatement': finance
    }
    
    return render(request, 'base/finance.html', context)

@login_required(login_url=('adminlogin', 'executivelogin'))
def activity(request):
    activity = Activity.objects.all()
    context = {
        'Activity': activity
    }
    
    return render(request, 'base/activity.html', context)


@login_required(login_url='executivelogin')  # Update the login URL
def profile(request):
    user = request.user
    executive_member = ExecutiveMember.objects.get(cid=user.cid)

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            user.profile_pic = form.cleaned_data['profile_pic']
            user.save()
            return redirect('profile')

    else:
        form = ProfilePictureForm()

    context = {
        'name': executive_member.name,
        'present_address': executive_member.present_address,
        'village': executive_member.village,
        'geog': executive_member.geog,
        'dzongkhag': executive_member.dzongkhag,
        'cid': executive_member.cid,
        'email': executive_member.email,
        'contact_no': executive_member.contact_no,
        'responsibility': executive_member.responsibility,
        'form': form,  # Add the form to the context
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

import openpyxl
from django.db import IntegrityError

def bulk_upload(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb.active

        headers = [cell.value for cell in sheet[1]]  # Get the header values

        for row in sheet.iter_rows(min_row=2, values_only=True):
            data = dict(zip(headers, row))  # Map header values to row values
            print(data)

            # Extract the relevant attributes from the data dictionary
            cid = int(data.get('cid', '')) if data.get('cid') else None
            name = data.get('name', '')
            responsibility = data.get('responsibility', '')
            present_address = data.get('present_address', '')
            contact_no = int(data.get('contact_no', '')) if data.get('cid') else None
            village = data.get('village', '')
            geog = data.get('geog', '')
            dzongkhag = data.get('dzongkhag', '')
            stage_of_threma = data.get('stage_of_threma', '')

            try:
                practitioner = Practitioner.objects.create(
                    cid=cid,
                    name=name,
                    responsibility=responsibility,
                    present_address=present_address,
                    contact_no=contact_no,
                    village=village,
                    geog=geog,
                    dzongkhag=dzongkhag,
                    stage_of_threma=stage_of_threma
                )
            except IntegrityError:
                continue  # Ignore the row with null cid and move to the next row

        return redirect('practitioner')  # Redirect to the practitioner page

    else:
        form = BulkUploadForm()

    return render(request, 'base/practitioner.html', {'form': form})



def export_practitioners(request):
    practitioners = Practitioner.objects.all()
    data = {
        'CID': [practitioner.cid for practitioner in practitioners],
        'Name': [practitioner.name for practitioner in practitioners],
        'Responsibility': [practitioner.responsibility for practitioner in practitioners],
        'Present Address': [practitioner.present_address for practitioner in practitioners],
        'Contact No': [practitioner.contact_no for practitioner in practitioners],
        'Village': [practitioner.village for practitioner in practitioners],
        'Geog': [practitioner.geog for practitioner in practitioners],
        'Dzongkhag': [practitioner.dzongkhag for practitioner in practitioners],
        'Stage of Threma': [practitioner.stage_of_threma for practitioner in practitioners],
        'Is Active': [practitioner.is_active for practitioner in practitioners],
    }

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=practitioners.xlsx'
    df.to_excel(response, index=False)

    return response



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


# def display_member_info(request):
#     if request.method == 'GET':
#         cid = request.GET.get('cid')
#         try:
#             member = get_object_or_404(Practitioner, cid=cid)
#             data = {
#                 'member': {
#                     'name': member.name,
#                     'contact_no': member.contact_no,
#                     'present_address': member.present_address,
#                 }
#             }
#             return JsonResponse(data)
#         except ExecutiveMember.DoesNotExist:
#             return JsonResponse({'error': 'Member not found.'})

#     return JsonResponse({'error': 'Invalid request method.'})

# def submit_transfer_form(request):
#     if request.method == 'POST':
#         form = TransferForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('transferform')  # Redirect to a success page
#     else:
#         form = TransferForm()
#     return render(request, 'base/transferform.html', {'form': form})


def display_member_info(request):
    cid = request.GET.get('cid')
    try:
        member = Practitioner.objects.get(cid=cid)
        data = {
            'member': {
                'cid': member.cid,
                'name': member.name,
                'contact_no': member.contact_no,
                'present_address': member.present_address
            }
        }
    except Practitioner.DoesNotExist:
        data = {'error': 'Member not found.'}
    
    return JsonResponse(data)

def submit_transfer_form(request):
    if request.method == 'POST':
        cid = request.POST.get('cid')
        reason = request.POST.get('reason')
        
        try:
            practitioner = Practitioner.objects.get(cid=cid)
            transfer = Transfer.objects.create(practitioner=practitioner, reason=reason)
            transfer.save()
            
            messages.success(request, 'Transfer form submitted successfully.')
            return redirect('transferform')
        except Practitioner.DoesNotExist:
            return JsonResponse({'error': 'Member not found.'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
    return JsonResponse({'error': 'Invalid request method.'})

def edit_member(request, member_cid):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        responsibility = request.POST.get('responsibility')
        present_address = request.POST.get('present_address')
        contact_no = request.POST.get('contact_no')
        card_no = request.POST.get('card_no')
        village = request.POST.get('village')
        geog = request.POST.get('geog')
        dzongkhag = request.POST.get('dzongkhag')
        role = request.POST.get('role')

        try:
            member = ExecutiveMember.objects.get(cid=member_cid)
            member.name = name
            member.email = email
            member.responsibility = responsibility
            member.present_address = present_address
            member.contact_no = contact_no
            member.card_no = card_no
            member.village = village
            member.geog = geog
            member.dzongkhag = dzongkhag
            member.role = role
            member.save()
            return redirect('executives')  # Redirect to the executives page or any other desired URL
        except ExecutiveMember.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Member not found'})


    return redirect('base/executives.html')  # Redirect to the homepage or any other desired URL

def edit_practitioner(request, member_cid):
    if request.method == 'POST':
        name = request.POST.get('name')
        responsibility = request.POST.get('responsibility')
        present_address = request.POST.get('present_address')
        contact_no = request.POST.get('contact_no')
        village = request.POST.get('village')
        geog = request.POST.get('geog')
        dzongkhag = request.POST.get('dzongkhag')
        stage_of_threma = request.POST.get('stage_of_threma')

        try:
            member = Practitioner.objects.get(cid=member_cid)
            member.name = name
            member.responsibility = responsibility
            member.present_address = present_address
            member.contact_no = contact_no
            member.village = village
            member.geog = geog
            member.dzongkhag = dzongkhag
            member.stage_of_threma = stage_of_threma
            member.save()
            return redirect('practitioner')  # Redirect to the executives page or any other desired URL
        except ExecutiveMember.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Member not found'})


    return redirect('base/practitioner.html')  # Redirect to the homepage or any other desired URL




def delete_member(request, member_cid):
    if request.method == 'POST':
        member = get_object_or_404(ExecutiveMember, cid=member_cid)
        member.delete()
        return redirect(reverse('executives'))  # Redirect to the executives page after deletion
    else:
        return redirect(reverse('executives'))  # Redirect to the executives page if the request method is not POST

def delete_practitioner(request, member_cid):
    if request.method == 'POST':
        member = get_object_or_404(Practitioner, cid=member_cid)
        member.delete()
        return redirect(reverse('practitioner'))  # Redirect to the executives page after deletion
    else:
        return redirect(reverse('practitioner'))  # Redirect to the executives page if the request method is not POST

def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            backend = CustomBackend()
            backend.change_password(request.user, new_password)
            # Optionally, you can authenticate the user with the new password
            authenticated_user = authenticate(request, cid=request.user.cid, password=new_password, role=request.user.role)
            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, 'Your password has been changed successfully.')
                return redirect('index')  # Redirect to a success page
            else:
                # Handle authentication failure if necessary
                messages.error(request, 'Failed to authenticate with the new password.')
        else:
            # Form submission has errors
            errors = form.errors.get_json_data()
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'main.html', {'form': form})


def semso(request):
    semso_entries = Semso.objects.all()
    context = {'Semso': semso_entries}
    return render(request, 'base/semso.html', context)

def add_semso(request):
    if request.method == 'POST':
        form = SemsoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('semso')  # Replace 'success_page' with the URL or name of the success page
    else:
        form = SemsoForm()
    
    context = {'form': form}
    return render(request, 'base/semso.html', context)



def logout_view(request):
    user = request.user
    logout(request)

    if user.is_authenticated and user.is_superuser:
        return redirect('admin_login')  # Replace 'admin_login' with the desired admin login URL
    else:
        return redirect('executive_login')  # Replace 'executive_login' with the desired executive login URL


def home(request):
    return render(request, 'ui/home.html')


    
def aboutus(request):
    return render(request, 'ui/aboutus.html')

def uifinance(request):
    statements = FinancialStatement.objects.all()
    context = {
        'statements': statements
        }
    return render(request, 'ui/uifinance.html', context)

def uiactivity(request):
    # Retrieve in-progress activities
    activity = Activity.objects.all()

    
    in_progress_activities = Activity.objects.filter(status='PENDING')

    # Retrieve completed activities
    completed_activities = Activity.objects.filter(status='COMPLETED')

    context = {
        'in_progress_activities': in_progress_activities,
        'completed_activities': completed_activities,
        'Activity': activity
    }

    return render(request, 'ui/uiactivity.html', context)
    
def uisemso(request):
    semso_data = Semso.objects.all()
    return render(request, 'ui/uisemso.html', {'semso_data': semso_data})