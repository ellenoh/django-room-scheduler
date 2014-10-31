
from django import forms

from room_scheduler.renters.models import Renter


class RenterForm(forms.ModelForm):
    class Meta:
        model = Renter
        fields = ('email', 'mobile_phone_number', 'home_phone_number', 'contact_info_visible')
        
