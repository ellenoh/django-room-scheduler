
import datetime

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models

from room_scheduler import settings


class TimeSlotManager(models.Manager):
    def get_all_for_month_for_renter(self, year, month, renter):
        self.renter = User.objects.get(username=renter).get_profile()
        return TimeSlot.objects.all().filter(date__month=month, date__year=year, renter=self.renter)

    def all_future_reservations(self):
        return TimeSlot.objects.all().filter(renter__isnull=False,
                                             date__gte=datetime.date.today())


class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    renter = models.ForeignKey('renters.Renter', null=True, blank=True)
    when_reserved = models.DateTimeField(null=True, blank=True)
    can_be_changed_by_renter = models.BooleanField(default=True)

    objects = TimeSlotManager()

    def __unicode__(self):
        if self.renter:
            return u"From %s to %s on %s (reserved by %s %s)" % (self.start_time.strftime("%I:%M"), self.end_time.strftime("%I:%M"), self.date.strftime("%m-%d-%Y"), self.renter.first_name, self.renter.last_name )
        else:
            return u"From %s to %s on %s" % (self.start_time.strftime("%I:%M"), self.end_time.strftime("%I:%M"), self.date.strftime("%m-%d-%Y"))

    @property
    def start_time_and_date(self):
        return datetime.datetime(self.date.year, self.date.month, self.date.day, self.start_time.hour, self.start_time.minute, self.start_time.second)

    @property
    def end_time_and_date(self):
        return datetime.datetime(self.date.year, self.date.month, self.date.day, self.end_time.hour, self.end_time.minute, self.end_time.second)

    def can_reserve(self, requester, renter):
        if self.renter:
            return (False, 'This timeslot is already reserved.')
        month = self.date.month
        year = self.date.year
        if not renter.calculate_available_credits_for_month(month, year) > 0:
            return (False, "You don't have enough credits to reserve that timeslot.")
        if requester.is_superuser:
            return (True, '')
        if self.start_time_and_date < datetime.datetime.now():
            return (False, 'It is too late to reserve this timeslot.')
        if self.date > renter.can_view_or_change_up_to:
            return (False, "You can't reserve a timeslot that far in advance.")
        return (True, '')

    def can_unreserve(self, requester, renter):
        if not self.renter:
            return (False, "This timeslot isn't reserved")
        if requester.is_superuser:
            return (True, '')
        if requester.username != self.renter.username:
            return (False, "You cannot unreserve someone else's timeslot")
        if self.start_time_and_date < datetime.datetime.now():
            return (False, '')
        if not renter.flexible_renter:
            return (False, '')
        if (self.start_time_and_date - datetime.timedelta(hours=settings.NO_CANCELATION_PERIOD)) < datetime.datetime.now():
            if (self.when_reserved + datetime.timedelta(minutes=settings.GRACE_PERIOD_FOR_SAME_DAY_RESERVATIONS)) > datetime.datetime.now():
                return (True, '')
            else:
                return (False, "I'm sorry, but it's too late to unreserve this spot.")
        if self.date > renter.can_view_or_change_up_to:
            return (False, "Sorry, that's too far in the future to change.")
        return (True, '')   

    def overlap(self, rival):
        if (rival.start_time < self.start_time) & (rival.end_time > self.start_time):
            return True
        if (rival.start_time < self.end_time) & (rival.end_time > self.start_time):
            return True
        return False

    def overlaps_with_existing_time_slot(self):
        # all_time_slots_that_day = TimeSlot.objects.all().filter(date=self.date)
        # if not all_time_slots_that_day:
        #     return False
        # for time_slot in all_time_slots_that_day:
        #     if self.overlap(time_slot):
        #         return True
        # return False
        potential_rivals = TimeSlot.objects.all().filter(start_time__gte=self.start_time, date=self.date)
        if not potential_rivals:
            return False
        for time_slot in potential_rivals:
            if self.overlap(time_slot) and self is not time_slot:
                return True

        return False
    
    def is_coherent(self):
        if (self.start_time >= self.end_time):
            return False
        else:
            return True
        return False        

    def check_valid_to_create(self):
        if not self.is_coherent():
            return False
        if self.overlaps_with_existing_time_slot():
            return False
        return True
        
    # def save(self):
    #     if self.pk or self.check_valid_to_create():
    #         super(TimeSlot, self).save()
    #     else:            
    #         raise PermissionDenied


class TimeSlotHistory(models.Model):
    saver = models.ForeignKey('renters.Renter', related_name='saver', null=True, blank=True)
    saved_for = models.ForeignKey('renters.Renter', related_name='saved_for')
    time_slot = models.ForeignKey('timeslots.TimeSlot')
    datetime_of_change = models.DateTimeField(default=datetime.datetime.now)
    reserved = models.BooleanField()

    class Meta:
        ordering = ('-datetime_of_change',)


def check_can_add_multiple_time_slots(start_date, end_date, start_time, end_time, isoweekday):
    all_time_slots_in_period = TimeSlot.objects.all().filter(date__gte=start_date, date__lte=end_date)
    roving_date = start_date
    while roving_date < end_date + datetime.timedelta(1):
        if not (int(isoweekday) == roving_date.isoweekday()):
            pass
        else:
            new_time_slot = TimeSlot(start_time=start_time,
                                     end_time=end_time,
                                     date=roving_date)
            if not new_time_slot.check_valid_to_create():
                return False
        roving_date = roving_date + datetime.timedelta(1)
    return True


def check_can_delete_multiple_time_slots(start_date, end_date, start_time, end_time, day_of_week):
    #Make sure there aren't any renters associated with the time slots.
    all_time_slots_in_period = TimeSlot.objects.all().filter(date__gte=start_date, date__lte=end_date, start_time=start_time, end_time=end_time)
    for time_slot in all_time_slots_in_period:
        if time_slot.renter and time_slot.isoweekday==day_of_week:
            return False
    return True

def delete_multiple_time_slots(start_date, end_date, start_time, end_time, day_of_week):
    if not check_can_delete_multiple_time_slots(start_date, end_date, start_time, end_time, day_of_week):
        raise PermissionDenied
    roving_date = start_date
    while roving_date < end_date + datetime.timedelta(1):
        if not (int(isoweekday) == roving_date.isoweekday()):
            pass
        else:
            time_slot_to_delete = TimeSlot(start_time=start_time,
                                     end_time=end_time,
                                     date=roving_date)
            time_slot_to_delete.delete()
        roving_date = roving_date + datetime.timedelta(1)



def canAddRenterToMultipleTimeSlots(start_date, end_date, start_time, end_time, day_of_week):
    # all_existing_slots = TimeSlot.objects.all().filter(date__gte=start_date, date__lte=end_date, renter, fixed)
    pass

def canDeleteRenterFromMultipleTimeSlots(start_date, end_date, start_time, end_time, day_of_week):
    # all_existing_slots = TimeSlot.objects.all().filter(date__gte=start_date, date__lte=end_date, renter)
    pass



# class RepeatingTimeSlot(models.Model):
#     """Allows for easy bulk addition and removal of timeslots for a
#     specified date range.  Note that a time slot that has a
#     reservation cannot be deleted this way."""

#     DAY_OF_WEEK_CHOICES = (
#         ('1', 'Monday'),
#         ('2', 'Tuesday'),
#         ('3', 'Wednesday'),
#         ('4', 'Thursday'),
#         ('5', 'Friday'),
#         ('6', 'Saturday'),
#         ('7', 'Sunday'),
#         )
    

#     def check_all_valid_to_create(self):
#         roving_date = self.start_date
#         while roving_date < self.end_date + datetime.timedelta(1):
#             if int(self.day_of_the_week) == roving_date.isoweekday():
                

#                 new_time_slot = TimeSlot(start_time = self.start_time,
#                                          end_time = self.end_time,
#                                          date = roving_date)
#                 if not new_time_slot.check_valid_to_create():
#                     return False
#             roving_date = roving_date + datetime.timedelta(1)
#         return True



#     def save(self):
#         if self.check_all_valid_to_create():
#             self.check_all_valid_to_create()
#             roving_date = self.start_date
#             while roving_date < self.end_date + datetime.timedelta(1):
#                 if int(self.day_of_the_week) == roving_date.isoweekday():
#                     new_time_slot = TimeSlot(start_time = self.start_time,
#                                              end_time = self.end_time,
#                                              date = roving_date)
#                     new_time_slot.save()
#                 else:
#                     pass
#                 roving_date = roving_date + datetime.timedelta(1)
#             super(RepeatingTimeSlot, self).save()
#         else:
#             raise PermissionDenied

#     def delete(self):
#         roving_date = self.start_date
#         while roving_date < self.end_date + datetime.timedelta(1):
#             if int(self.day_of_the_week) == roving_date.isoweekday():
#                 try:
#                     time_slot = TimeSlot.objects.get(start_time = self.start_time,
#                                                      end_time = self.end_time,
#                                                      date = roving_date)
#                     time_slot.delete()
#                 except:
#                     pass
#             else:
#                 pass
#             roving_date = roving_date + datetime.timedelta(1)
#         super(RepeatingTimeSlot, self).delete()

# class RepeatingReservation(models.Model):

#     renter = models.ForeignKey('renters.Renter')
#     repeating_time_slot = models.ForeignKey(TimeSlot, unique=True)

#     def __unicode__(self):
#         return u"Repeating Reservation for %s %s on %s" % (
#             self.renter.first_name,
#             self.renter.last_name,
#             self.repeating_time_slot,
#             )


#     # def save(self):
#     #     roving_date = self.start_date
#     #     while roving_date < self.end_date + datetime.timedelta(1):
#     #         if int(self.day_of_the_week) == roving_date.isoweekday():
#     #             roving_time_slot = TimeSlot.objects.get(start_time = self.start_time,
#     #                                                     end_time = self.end_time,
#     #                                                     date = roving_date)
#     #             new_reservation = Reservation(renter=self.renter,
#     #                                           time_slot=roving_time_slot)
#     #             new_reservation.save()
#     #         else:
#     #             pass
#     #         roving_date = roving_date + datetime.timedelta(1)
#     #     super(RepeatingReservation, self).save()
        
            
#     # def delete(self):
#     #     roving_date = self.start_date
#     #     while roving_date < self.end_date + datetime.timedelta(1):
#     #         if int(self.day_of_the_week) == roving_date.isoweekday():
#     #             roving_time_slot = TimeSlot.objects.get(start_time = self.start_time,
#     #                                                     end_time = self.end_time,
#     #                                                     date = roving_date)
#     #             new_reservation = Reservation.objects.get(renter=self.renter,
#     #                                           time_slot=roving_time_slot)
#     #             new_reservation.delete()
#     #         else:
#     #             pass
#     #         roving_date = roving_date + datetime.timedelta(1)
#     #     super(RepeatingReservation, self).delete()
        

