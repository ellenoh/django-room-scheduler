
from django import forms

from room_scheduler.renters.models import Renter


DAY_OF_WEEK_CHOICES = (
    ('1', 'Monday'),
    ('2', 'Tuesday'),
    ('3', 'Wednesday'),
    ('4', 'Thursday'),
    ('5', 'Friday'),
    ('6', 'Saturday'),
    ('7', 'Sunday'),
    )


class RepeatingTimeSlotCreateForm(forms.Form):
    start_date = forms.DateField(help_text="(E.g., '2009-09-01')")
    end_date = forms.DateField(help_text="(E.g., '2009-09-01')")
    start_time = forms.TimeField(help_text="(E.g., '09:00:00' or '15:00:00')")
    end_time = forms.TimeField(help_text="(E.g., '09:00:00' or '15:00:00')")
    day_of_week = forms.ChoiceField(choices=DAY_OF_WEEK_CHOICES)


class RepeatingTimeSlotDeleteForm(forms.Form):
    start_date = forms.DateField(help_text="(E.g., '2009-09-01')")
    end_date = forms.DateField(help_text="(E.g., '2009-09-01')")
    start_time = forms.TimeField(help_text="(E.g., '09:00:00' or '15:00:00')")
    end_time = forms.TimeField(help_text="(E.g., '09:00:00' or '15:00:00')")
    day_of_week = forms.ChoiceField(choices=DAY_OF_WEEK_CHOICES)


class RepeatingRentalCreateForm(forms.Form):
    start_date = forms.DateField(help_text="(E.g., '2009-09-01')")
    end_date = forms.DateField(help_text="(E.g., '2009-09-01')")
    start_time = forms.TimeField(help_text="(E.g., '09:00:00' or '15:00:00')")
    end_time = forms.TimeField(help_text="(E.g., '09:00:00' or '15:00:00')")
    renter = forms.ModelChoiceField(queryset=Renter.objects.all())
    can_be_changed_by_renter = forms.BooleanField()
    day_of_week = forms.ChoiceField(choices=DAY_OF_WEEK_CHOICES)


class RepeatingRentalDeleteForm(forms.Form):
    start_date = forms.DateField(help_text="(E.g., '2009-09-01')")
    end_date = forms.DateField(help_text="(E.g., '2009-09-01')")
    start_time = forms.TimeField(help_text="(E.g., '09:00:00' or '15:00:00')")
    end_time = forms.TimeField(help_text="(E.g., '09:00:00' or '15:00:00')")
    renter = forms.ModelChoiceField(queryset=Renter.objects.all())
    can_be_changed_by_renter = forms.BooleanField()
    day_of_week = forms.ChoiceField(choices=DAY_OF_WEEK_CHOICES)
