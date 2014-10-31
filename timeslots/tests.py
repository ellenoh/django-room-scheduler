
import datetime
import unittest

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from room_scheduler.renters.models import Renter
from room_scheduler.timeslots.models import TimeSlot
from room_scheduler.timeslots.models import check_can_add_multiple_time_slots, check_can_delete_multiple_time_slots


class TestTimeSlot(unittest.TestCase):    
    def setUp(self):
        self.start_time = datetime.time(11,0)
        self.end_time = datetime.time(12,0)
        self.today = datetime.date.today()
        self.last_month = datetime.date.today() - datetime.timedelta(30)
        self.next_month = datetime.date.today() + datetime.timedelta(30)
        self.two_months_from_now = datetime.date.today() + datetime.timedelta(60)

        self.time_slot = TimeSlot(start_time=self.start_time, end_time=self.end_time, date=self.today)
        self.time_slot.save()
        self.day_of_week = self.time_slot.date.isoweekday()

        self.renter_user = User(username='andy', password='a', is_superuser=False)

        self.renter = Renter(user=self.renter_user,
                                       first_name = 'Andy',
                                       last_name = 'Doe',
                                       email = 'j@j.com',
                                       permitted_rentals_per_month = 4,
                                       account_expires = self.two_months_from_now,
                                       )


    # def test_time_slot_should_not_start_after_it_ends(self):
    #     self.incoherent_time_slot = TimeSlot(start_time=self.end_time, end_time=self.start_time, date=self.today)
    #     self.assertRaises(PermissionDenied, self.incoherent_time_slot.save)

    def test_time_slot_can_be_resaved(self):
        self.time_slot.save()

    def test_overlap_should_return_true_if_rival_starts_before_start_and_ends_after_start(self):
        rival = TimeSlot(start_time=datetime.time(10,59), end_time=datetime.time(11,01), date=self.today)
        self.assertEquals(self.time_slot.overlap(rival), True)
    
    def test_overlap_should_return_true_if_rival_starts_before_end_and_ends_after_start(self):
        rival = TimeSlot(start_time=datetime.time(11,30), end_time=datetime.time(11,01), date=self.today)
        self.assertEquals(self.time_slot.overlap(rival), True)
        
    def test_overlap_should_return_true_if_rival_starts_at_and_ends_at(self):
        rival = TimeSlot(start_time=self.start_time, end_time=self.end_time, date=self.today)
        self.assertEquals(self.time_slot.overlap(rival), True)
        
    def test_overlap_should_return_false_if_rival_starts_before_and_ends_before(self):
        rival = TimeSlot(start_time=datetime.time(9,0), end_time=datetime.time(10,0), date=self.today)
        self.assertEquals(self.time_slot.overlap(rival), False)

    def test_overlaps_should_return_false_if_rival_ends_after_and_ends_after(self):
        rival = TimeSlot(start_time=datetime.time(13,0), end_time=datetime.time(14,0), date=self.today)
        self.assertEquals(self.time_slot.overlap(rival), False)

    # def test_time_slot_should_not_save_if_it_overlaps_with_another_time_slot(self):
    #     overlapping_rival = TimeSlot(start_time=datetime.time(10,59), end_time=datetime.time(11,01), date=self.today)
    #     self.assertRaises(PermissionDenied, overlapping_rival.save)
        

    #Adding multiple time slots

    # def test_can_add_multiple_time_slots_should_return_false_if_any_time_slot_overlaps_with_existing_time_slot(self):
    #     self.assertEquals(check_can_add_multiple_time_slots(self.last_month,
    #                                                         self.next_month,
    #                                                         datetime.time(10,59),
    #                                                         datetime.time(11,01),
    #                                                         str(self.day_of_week)), False)


    # def test_check_can_delete_multiple_time_slot_should_return_false_if_any_time_slot_already_rented(self):
    #     self.time_slot.renter = self.renter
    #     self.time_slot.save()
    #     self.assertEquals(check_can_delete_multiple_time_slots(self.last_month,
    #                                                            self.next_month,
    #                                                            self.time_slot.start_time,
    #                                                            self.time_slot.end_time,
    #                                                            str(self.day_of_week)), False)

    # def test_adding_renter_to_multiple_time_slots_should_fail_if_not_all_time_slots_exist(self):
    #     add_multiple_time_slots(self.last_month,
    #                             self.next_month,
    #                             self.time_slot.start_time,
    #                             self.time_slot.end_time,
    #                             str(self.day_of_week)
    #     slot_to_destroy = TimeSlot.objects.get(start_time=self.time_slot.start_time,
    #                                            end_time=self.time_slot.end_time,
    #                                            date=self.last_month)
    #     slot_to_destroy.delete()
    #     add_renter_to_multiple_time_slots(self.last_month,
    #                                       self.next_month,
    #                                       self.time_slot.start_time,
    #                                       self.time_slot.end_time,
    #                                       str(self.day_of_week),
    #                                       self.renter)

    def test_adding_renter_to_multiple_time_slots_should_fail_if_any_time_slot_already_rented(self):
        pass

