
import datetime

from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db import models

from room_scheduler import settings
from room_scheduler.timeslots.models import TimeSlot


class Renter(models.Model):
    user = models.ForeignKey(User, unique=True)
    first_name = models.CharField('first name', max_length=30)
    last_name = models.CharField('last name', max_length=30)
    email = models.EmailField('e-mail address', null=True, blank=True)
    extra_credits = models.IntegerField(default=0)
    permitted_rentals_per_month = models.IntegerField()
    can_see_days_ahead = models.IntegerField(default=60)
    flexible_renter = models.BooleanField(default=True)
    account_expires = models.DateField()
    contact_info_visible = models.BooleanField(default=True)
    mobile_phone_number = PhoneNumberField(null=True, blank=True)
    home_phone_number = PhoneNumberField(null=True, blank=True)
    email_notifications = models.BooleanField(help_text="(Do you want an email notification after you make a reservation?", default=False)

    class Meta:
        ordering = ['last_name', 'first_name']

    @models.permalink
    def get_absolute_url(self):
        return ('renter_index', (), {
            'renter': self.username,
            })

    def get_edit_page(self):
        return "/admin/auth/user/%d" % self.user.pk

    def calculate_available_credits_for_month(self, month, year):
        month = int(month)
        year = int(year)
        today = datetime.date.today()
        first_day_of_current_month = datetime.date(today.year, today.month, 1)
        first_day_of_date_month = datetime.date(year, month, 1)
        if first_day_of_date_month < first_day_of_current_month:
            return 0
        reservations = TimeSlot.objects.all().filter(date__year=year, date__month=month, renter=self)
        return self.permitted_rentals_per_month - len(reservations) + self.extra_credits

    @property
    def future_time_slots(self):
        return TimeSlot.objects.all().filter(date__gte=datetime.date.today(), renter=self).order_by('date')

    @property
    def past_time_slots(self):
        return TimeSlots.objects.all().filter(date__lte=datetime.date.today(), renter=self).order_by('date')

    @property
    def can_view_or_change_up_to(self):
        cut_off_date = datetime.date.today() + datetime.timedelta(self.can_see_days_ahead)
        if cut_off_date > self.account_expires:
            return self.account_expires
        else:
            return cut_off_date

    @property
    def account_active(self):
        if datetime.date.today() > self.account_expires:
            return False
        return True

    @property
    def username(self):
        return self.user.username

    @property
    def full_name(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def save(self):
        """I prefer to use the User Profile ONLY for authentication.
        However, I want to make sure that names and emails show up in
        the admin view, so I'll just make sure that names and emails
        are properly stashed on the User instance too when the renter
        is created or updated."""
        self.user.first_name = self.first_name
        self.user.last_name = self.last_name
        self.user.email = self.email
        self.user.save()
        super(Renter, self).save()

    def delete(self):
        """ We really don't want a time slot deleted just because we
        deleted the renter who had a reservation to it, NOT that we
        should be deleting renters. Still.  Note that we also altered
        the admin template that warns about the deletion of time slots
        when you delete a renter."""
        try:
            time_slots_for_renter = TimeSlot.objects.all().filter(renter=self)
            for time_slot in time_slots_for_renter:
                time_slot.renter = None
                time_slot.save()
        except:
            pass
        super(Renter, self).delete()
