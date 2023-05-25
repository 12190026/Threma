from django import forms
from django.forms import ModelForm, Form
from .models import ExecutiveMember, Practitioner, Activity, FinancialStatement, TransferForm, Semso
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

class ExecutiveMemberForm(ModelForm):
    
    class Meta:
        model = ExecutiveMember
        fields = '__all__'
        # Exclude any fields that do not need validation.

    def clean_cid(self):
        # Check if the CID is exactly 11 characters long.
        cid = self.cleaned_data['cid']
        if len(cid) != 11:
            raise forms.ValidationError('CID must be exactly 11 characters long.')
        return cid

    def clean_contact_no(self):
        # Check if the contact number is exactly 8 digits long.
        contact_no = self.cleaned_data['contact_no']
        if len(contact_no) != 8:
            raise forms.ValidationError('Contact number must be exactly 8 digits long.')
        return contact_no

    def clean_email(self):
        # Check if the email is already in use.
        email = self.cleaned_data['email']
        if ExecutiveMember.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        # Add any other custom validation logic here.
        return cleaned_data

class ActivityForm(ModelForm):

    class Meta:
        model = Activity
        fields = ['name', 'description',  'image', 'date', 'time']

class ActivityStatusUpdateForm(ModelForm):
    class Meta:
        model = Activity
        fields = ['status']



class FinancialStatementForm(ModelForm):

    class Meta:
        model = FinancialStatement
        fields = '__all__'

class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize field labels, placeholders, or attributes if needed
        self.fields['old_password'].label = 'Old Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm Password'

        self.fields['old_password'].widget.attrs['placeholder'] = 'Enter your old password'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Enter your new password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm your new password'

    def clean(self):
        cleaned_data = super().clean()
        # Add custom validation if needed
        return cleaned_data


class LoginForm(Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': 'Invalid username or password.',
        'inactive': 'This account is inactive.',
    }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        # Check if the username and password are valid
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            elif not user.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return cleaned_data



class PractitionerForm(ModelForm):

    class Meta:
        model = Practitioner
        fields = '__all__'

class CidForm(Form):
    cid = forms.CharField()

class TransferForms(forms.ModelForm):
    class Meta:
        model = TransferForm
        fields = ['cid', 'name', 'email', 'contact_no', 'present_address', 'reason']

class ProfilePictureForm(Form):
    profile_pic = forms.ImageField()

class SemsoForm(ModelForm):
    class Meta:
        model = Semso
        fields = ['date', 'event', 'contributor', 'amount']

class BulkUploadForm(forms.Form):
    file = forms.FileField(label='Excel File')