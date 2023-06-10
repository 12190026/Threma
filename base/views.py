from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import  ExecutiveMember, Practitioner, Activity, FinancialStatement, Semso, Transfer
from .forms import ExecutiveMemberForm, PractitionerForm,  TransferForm, ActivityForm, FinancialStatementForm, ProfilePictureForm, PasswordChangeForm, SemsoForm, BulkUploadForm, ChangePasswordForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Count

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


@login_required(login_url='executivelogin') 
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

@login_required(login_url='executivelogin') 
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

@login_required(login_url='executivelogin') 
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


@login_required(login_url='executivelogin') 
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

@login_required(login_url='executivelogin') 
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

@login_required(login_url='executivelogin') 
def view_letter(request, transfer_id):
    transfer = get_object_or_404(Transfer, pk=transfer_id)
    practitioner = transfer.practitioner

    return render(request, 'base/transferform.html', {'practitioner': practitioner})

@login_required(login_url='executivelogin') 
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

@login_required(login_url='executivelogin') 
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


@login_required(login_url='executivelogin') 
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


@login_required(login_url='executivelogin') 
def update_activity_status(request, activity_id):
    activity = Activity.objects.get(activity_id=activity_id)
    if request.method == 'POST':
        activity.status = 'COMPLETED'  # replace with your desired logic
        activity.save()
    return redirect('activity')


@login_required(login_url='executivelogin') 
def executives(request):
    member = ExecutiveMember.objects.all().values()
    context = {
        'ExecutiveMember': member
    }

    return render(request, 'base/executives.html', context)

@login_required(login_url='executivelogin') 
def practitioner(request):
    member = Practitioner.objects.all().values()
    context = {
        'Practitioner': member
    }

    return render(request, 'base/practitioner.html', context)

@login_required(login_url='executivelogin') 
def add_member(request):
    if request.method == 'POST':
        form = ExecutiveMemberForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'success'})  # Send success response as JSON
        else:
            errors = form.errors.as_json()
            return JsonResponse(errors, status=400)  # Send form errors as JSON with status 400 (Bad Request)
    else:
        form = ExecutiveMemberForm()

    return render(request, 'base/executives.html', {'form': form})


@login_required(login_url='executivelogin') 
def search_executive_member(request):
    query = request.GET.get('q')
    if query:
        results = ExecutiveMember.objects.filter(name__icontains=query)
    else:
        results = None
    context = {'results': results}
    return render(request, 'base/executives.html', context)

@login_required(login_url='executivelogin')
def add_member_practitioner(request):
    if request.method == 'POST':
        form = PractitionerForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            cid = form.cleaned_data['cid']
            if Practitioner.objects.filter(cid=cid).exists():
                error_message = 'This CID already exists. Please choose a different one.'
                return JsonResponse({'error_message': error_message}, status=400)
            else:
                practitioner = form.save(commit=False)  # Create a new Practitioner instance without saving to the database yet
                if 'profile_pic' in request.FILES:  # Check if profile_pic file was uploaded
                    practitioner.profile_pic = request.FILES['profile_pic']  # Assign the uploaded file to the profile_pic field
                practitioner.save()  # Save the Practitioner instance to the database
                return JsonResponse({'message': 'success'})
        else:
            error_message = 'Form submission failed. Please check your input.'
            return JsonResponse({'error_message': error_message}, status=400)
    else:
        form = PractitionerForm()

    return render(request, 'base/practitioner.html', {'form': form})



import openpyxl
from django.db import IntegrityError
from datetime import datetime
from django.core.exceptions import ValidationError


@login_required(login_url='executivelogin') 
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
            cid = int(data.get('CID', '')) if data.get('CID') else None
            name = data.get('Name', '')
            tshogchung = data.get('Tshogchung', '')
            responsibility = data.get('Responsibility', '')
            present_address = data.get('Present Address', '')
            bob_str = data.get('BOB', '')
            bob_str = bob_str.strftime('%d/%m/%Y') if isinstance(bob_str, datetime) else bob_str
            contact_no = int(data.get('Contact No', '')) if data.get('CID') else None
            card_no = int(data.get('Card No', '')) if data.get('CID') else None
            village = data.get('Village', '')
            geog = data.get('Geog', '')
            dzongkhag = data.get('Dzongkhag', '')
            # stage_of_threma = data.get('stage_of_threma', '')

       
            try:
                bob = datetime.strptime(bob_str, '%d/%m/%Y').date() if bob_str else None
            except ValueError:
                raise ValidationError(f'Invalid date format for BOB: {bob_str}. It must be in DD/MM/YYYY format.')


            try:
                practitioner = Practitioner.objects.create(
                    cid=cid,
                    name=name,
                    tshogchung=tshogchung,
                    responsibility=responsibility,
                    present_address=present_address,
                    bob=bob,
                    contact_no=contact_no,
                    card_no=card_no,
                    village=village,
                    geog=geog,
                    dzongkhag=dzongkhag,
                    # stage_of_threma=stage_of_threma
                )
            except IntegrityError:
                continue  # Ignore the row with null cid and move to the next row

        return redirect('practitioner')  # Redirect to the practitioner page

    else:
        form = BulkUploadForm()

    return render(request, 'base/practitioner.html', {'form': form})


@login_required(login_url='executivelogin') 
def export_practitioners(request):
    practitioners = Practitioner.objects.all()
    data = {
        'CID': [practitioner.cid for practitioner in practitioners],
        'Name': [practitioner.name for practitioner in practitioners],
        'BOB': [practitioner.bob for practitioner in practitioners],
        'Responsibility': [practitioner.responsibility for practitioner in practitioners],
        'Present Address': [practitioner.present_address for practitioner in practitioners],
        'Contact No': [practitioner.contact_no for practitioner in practitioners],
        'Card No': [practitioner.card_no for practitioner in practitioners],
        'Village': [practitioner.village for practitioner in practitioners],
        'Geog': [practitioner.geog for practitioner in practitioners],
        'Dzongkhag': [practitioner.dzongkhag for practitioner in practitioners],
        'Stage of Threma': [practitioner.stage_of_threma for practitioner in practitioners],
    }

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=practitioners.xlsx'
    df.to_excel(response, index=False)

    return response



@login_required(login_url='executivelogin') 
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


@login_required(login_url='executivelogin')
def edit_statement(request, year):
    finance = get_object_or_404(FinancialStatement, year=year)

    if request.method == 'POST':
        try:
            # Handle the form submission and update the financial statement
            finance.image = request.FILES.get('image')
            finance.save()

            # Return a success response
            return JsonResponse({'success': True, 'message': 'Financial statement updated successfully'})
        except Exception as e:
            # Return an error response
            return JsonResponse({'success': False, 'message': str(e)})

    context = {
        'finance': finance
    }
    return render(request, 'base/finance.html', context)

def edit_semso(request, semso_id):
    semso = get_object_or_404(Semso, semso_id=semso_id)

    if request.method == 'POST':
        form = SemsoForm(request.POST, instance=semso)
        if form.is_valid():
            form.save()
            return redirect('semso')  # Redirect to the semso list page after successful update
    else:
        form = SemsoForm(instance=semso)

    return render(request, 'base/semso.html', {'form': form, 'semso': semso})

def delete_semso(request, semso_id):
    semso = get_object_or_404(Semso, semso_id=semso_id)

    if request.method == 'POST':
        semso.delete()
        return redirect('semso')  # Redirect to the list view after deletion

    return render(request, 'base/semso.html', {'semso': semso})

def delete_transfer(request, practitioner):
    transfer = get_object_or_404(Transfer, practitioner=practitioner)

    if request.method == 'POST':
        transfer.delete()
        return redirect('transferform')  # Redirect to the list view after deletion

    return render(request, 'base/transferform.html', {'transfer': transfer})

def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, activity_id=activity_id)

    if request.method == 'POST':
        # Handle the form submission for editing the activity
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        date = request.POST.get('date')
        time = request.POST.get('time')

        try:
            # Update the activity fields
            activity.name = name
            activity.description = description
            if image:
                activity.image = image
            activity.date = date
            activity.time = time
            activity.save()
            # Redirect to the activity list or show a success message
            return redirect('activity')
        except:
            return JsonResponse({'success': False, 'activity': 'Activity not found'})

    return render(request, 'base/activity.html', {'activity': activity})

    
def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    if request.method == 'POST':
        # Delete the activity
        activity.delete()

        # Redirect to the activity list or show a success message
        return redirect('activity')

    context = {'activity': activity}
    return render(request, 'base/activity.html', context)

def upload_statement(request):
    if request.method == 'POST':
        form = FinancialStatementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Financial statement added successfully.'})
        else:
            return JsonResponse({'error': 'Error occurred while adding Financial Statement. Please try again.'})
    else:
        form = FinancialStatementForm()

    year_choices = [year for year in range(2015, 2031)]
    context = {'form': form, 'year_choices': year_choices}
    return JsonResponse(context)


@login_required(login_url='executivelogin') 
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

@login_required(login_url='executivelogin') 
def submit_transfer_form(request):
    if request.method == 'POST':
        cid = request.POST.get('cid')
        reason = request.POST.get('reason')
        
        try:
            practitioner = Practitioner.objects.get(cid=cid)
            transfer = Transfer.objects.create(practitioner=practitioner, reason=reason)
            transfer.save()
            
            return JsonResponse({'success': 'Transfer form submitted successfully.'})
        except Practitioner.DoesNotExist:
            return JsonResponse({'error': 'Member not found.'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
    return JsonResponse({'error': 'Invalid request method.'})


@login_required(login_url='executivelogin')
def edit_statement(request, year):
    finance = get_object_or_404(FinancialStatement, year=year)

    if request.method == 'POST':
        # Handle the form submission and update the financial statement
        finance.year = request.POST.get('year')
        finance.image = request.FILES.get('image')
        finance.save()

        # Redirect to the appropriate page after editing the financial statement
        return redirect('finance')

    context = {
        'finance': finance
    }
    return render(request, 'base/finance.html', context)




@login_required(login_url='executivelogin')
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
            return JsonResponse({'success': True, 'message': 'Member data updated successfully'})
        except ExecutiveMember.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Member not found'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def edit_practitioner(request, member_cid):
    if request.method == 'POST':
        # Retrieve the form data
        name = request.POST.get('name')
        responsibility = request.POST.get('responsibility')
        profile_pic = request.FILES.get('profile_pic')
        bob = request.POST.get('bob')
        present_address = request.POST.get('present_address')
        contact_no = request.POST.get('contact_no')
        card_no = request.POST.get('card_no')
        village = request.POST.get('village')
        tshogchung = request.POST.get('tshogchung')
        geog = request.POST.get('geog')
        dzongkhag = request.POST.get('dzongkhag')
        stage_of_threma = request.POST.get('stage_of_threma')

        try:
            member = Practitioner.objects.get(cid=member_cid)
            member.name = name
            member.responsibility = responsibility
            member.bob = bob
            member.present_address = present_address
            member.contact_no = contact_no
            member.card_no = card_no
            member.tshogchung = tshogchung
            member.village = village
            member.geog = geog
            member.dzongkhag = dzongkhag
            member.stage_of_threma = stage_of_threma

            # Check if a new profile picture is provided
            if profile_pic:
                member.profile_pic = profile_pic

            member.save()
            messages.success(request, 'Member updated successfully.')  # Success message
            return redirect('practitioner')  # Redirect to the practitioners page or any other desired URL
        except Practitioner.DoesNotExist:
            messages.error(request, 'Member not found.')  # Error message
            return redirect('practitioner')

    return redirect('base/practitioner.html')  # Redirect to the homepage or any other desired URL




@login_required(login_url='executivelogin') 
def delete_member(request, member_cid):
    if request.method == 'POST':
        member = get_object_or_404(ExecutiveMember, cid=member_cid)
        member.delete()
        return redirect(reverse('executives'))  # Redirect to the executives page after deletion
    else:
        return redirect(reverse('executives'))  # Redirect to the executives page if the request method is not POST

@login_required(login_url='executivelogin') 
def delete_practitioner(request, member_cid):
    if request.method == 'POST':
        member = get_object_or_404(Practitioner, cid=member_cid)
        member.delete()
        return redirect(reverse('practitioner'))  # Redirect to the executives page after deletion
    else:
        return redirect(reverse('practitioner'))  # Redirect to the executives page if the request method is not POST

def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == 'POST':
        # Delete the activity
        activity.delete()
        return redirect(reverse('activity'))  # Redirect to the executives page after deletion
    else:
        return redirect(reverse('activity'))  # Redirect to the executives page if the request method is not POST

def delete_statement(request, year):
    finance = get_object_or_404(FinancialStatement, year=year)

    if request.method == 'POST':
        # Delete the activity
        finance.delete()
        return redirect(reverse('finance'))  # Redirect to the executives page after deletion
    
    return render(request, 'base/finance.html', {'finance': finance})

@login_required(login_url='executivelogin') 
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Update session with new password

            messages.success(request, 'Your password has been changed successfully.')
            return redirect('index')  # Redirect to a success page
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'change_password.html', {'form': form})

@login_required(login_url='executivelogin') 
def semso(request):
    semso_entries = Semso.objects.all()
    context = {'Semso': semso_entries}
    return render(request, 'base/semso.html', context)

@login_required(login_url='executivelogin') 
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
        return redirect('adminlogin')  # Replace 'admin_login' with the desired admin login URL
    else:
        return redirect('executivelogin')  # Replace 'executive_login' with the desired executive login URL


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


#API

from rest_framework import viewsets
from .serializers import ExecutiveMemberSerializer, PractitionerSerializer, ActivitySerializer, FinancialStatementSerializer, TransferSerializer, SemsoSerializer

class ExecutiveMemberViewSet(viewsets.ModelViewSet):
    queryset = ExecutiveMember.objects.all()
    serializer_class = ExecutiveMemberSerializer

class PractitionerViewSet(viewsets.ModelViewSet):
    queryset = Practitioner.objects.all()
    serializer_class = PractitionerSerializer

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

class FinancialStatementViewSet(viewsets.ModelViewSet):
    queryset = FinancialStatement.objects.all()
    serializer_class = FinancialStatementSerializer

class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

class SemsoViewSet(viewsets.ModelViewSet):
    queryset = Semso.objects.all()
    serializer_class = SemsoSerializer
