from import_export import resources
from .models import Practitioner

class PractitionerResource(resources.ModelResource):
    class Meta:
        model = Practitioner
        fields = (
            'name',
            'responsibility',
            'present_address',
            'cid',
            'contact_no',
            'village',
            'geog',
            'dzongkhag',
            'stage_of_threma',
        )
