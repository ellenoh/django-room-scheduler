from django import forms

class ReservationForm(forms.Form):
    renter_username = forms.CharField(max_length=60)
    time_slot_pk = forms.IntegerField()

class DeleteRentalHistoryRecordForm(forms.Form):
    rental_history_record_pk = forms.IntegerField()
