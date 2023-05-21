from django.contrib import admin

# Register your models here.
from .models import ExecutiveMember, Practitioner, Activity, FinancialStatement, TransferForm, Semso

admin.site.register(ExecutiveMember)
admin.site.register(Practitioner)
admin.site.register(Activity)
admin.site.register(FinancialStatement)
admin.site.register(TransferForm)
admin.site.register(Semso)
