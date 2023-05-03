from django import forms
from django.forms import ModelForm
from .models import ExecutiveMember, Practitioner

class ExecutiveMemberForm(ModelForm):

    class Meta:
        model = ExecutiveMember
        fields = '__all__'

class PractitionerForm(ModelForm):

    class Meta:
        model = Practitioner
        fields = '__all__'
