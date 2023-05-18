from django.contrib import admin

# Register your models here.
from .models import ExecutiveMember, Practitioner, Activity, FinancialStatement

admin.site.register(ExecutiveMember)
admin.site.register(Practitioner)
admin.site.register(Activity)
admin.site.register(FinancialStatement)
