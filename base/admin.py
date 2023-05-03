from django.contrib import admin

# Register your models here.
from .models import ExecutiveMember, Practitioner

admin.site.register(ExecutiveMember)
admin.site.register(Practitioner)
