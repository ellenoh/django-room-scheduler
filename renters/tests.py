
import datetime
import os

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.http import HttpResponse
from django.test import TestCase, Client

from room_scheduler import settings
from room_scheduler.renters.models import Renter
from room_scheduler.renters.views import renter_detail, renter_account
from room_scheduler.timeslots.models import TimeSlot, TimeSlotHistory


os.environ['MEDIA_LOCATION'] = '/home/chris/code/ibeam_scheduler/media/'


class TestRenterPermissions(TestCase):
    def setUp(self):
        """We're testing the behaviour of three different renters: two renters
with regular accounts and one superuser renter.  They each have
related user accounts to handle authentication: 1) renter_user and
renter, 2) renter2_user and renter2, and 3 superuser and
super_renter."""

        self.today = datetime.date.today()
        self.yesterday = datetime.date.today() - datetime.timedelta(1)
        self.next_week = datetime.date.today() + datetime.timedelta(7)
        self.two_months_from_now = datetime.date.today() + datetime.timedelta(60)
        self.three_months_from_now = datetime.date.today() + datetime.timedelta(90)
        self.grace_period = settings.GRACE_PERIOD_FOR_SAME_DAY_RESERVATIONS
        self.too_late_to_unreserve = settings.NO_CANCELATION_PERIOD

        self.req = HttpRequest()

        self.timeslot_next_week = TimeSlot(start_time=datetime.time(9,00), end_time=datetime.time(11,00), date=self.next_week)
        self.timeslot_next_week.save()

        self.timeslot_yesterday = TimeSlot(start_time=datetime.time(9,00), end_time=datetime.time(11,00), date=self.yesterday)
        self.timeslot_yesterday.save()
        
        self.superuser = User(username='jane', password='a', is_superuser=True)
        self.superuser.save()

        self.super_renter = Renter(user=self.superuser,
                                       first_name = 'Jane',
                                       last_name = 'Doe',
                                       email = 'j@j.com',
                                       permitted_rentals_per_month = 8,
                                       account_expires = self.two_months_from_now,
                                       )
        self.super_renter.save()

        self.renter_user = User(username='john', password='a', is_superuser=False)
        self.renter_user.save()

        self.renter = Renter(user=self.renter_user,
                                       first_name = 'John',
                                       last_name = 'Doe',
                                       email = 'j@j.com',
                                       permitted_rentals_per_month = 4,
                                       account_expires = self.two_months_from_now,
                             
                                       )
        self.renter.save()
        
        self.renter2_user = User(username='janice', password='a', is_superuser=False)
        self.renter2_user.save()

        self.renter2 = Renter(user=self.renter2_user,
                                       first_name = 'Janice',
                                       last_name = 'Doe',
                                       email = 'j@j.com',
                                       permitted_rentals_per_month = 4,
                                       account_expires = self.two_months_from_now,
                                       )
        self.renter2.save()

        self.client = Client()

    def tearDown(self):
        pass

    def test_users_and_renters_can_be_created(self):
        self.assertEquals(User.objects.count(), 3)
        
    #View permissions

    def test_super_renter_should_be_able_to_view_own_page(self):
        self.req.user = self.superuser
        kwargs = {'request': self.req,
                  'renter': self.super_renter.username,
                  'year': self.today.year,
                  'month': self.today.month,
                  'day': self.today.day}
        response = renter_detail(**kwargs)
        self.assertEqual(response.status_code, 200)
        
    def anonymous_user_should_not_be_able_to_view_renter_page(self):
        kwargs = {'request': self.req,
                  'renter': self.renter.username,
                  'year': self.today.year,
                  'month': self.today.month,
                  'day': self.today.day}
        self.assertRaises(PermissionDenied, renter_detail, **kwargs)

    def test_super_renter_should_be_able_to_view_any_renter_page(self):
        self.req.user = self.superuser
        kwargs = {'request': self.req,
                  'renter': self.renter.username,
                  'year': self.today.year,
                  'month': self.today.month,
                  'day': self.today.day}
        response = renter_detail(**kwargs)
        self.assertEqual(response.status_code, 200)
        
    def test_renter_should_be_able_to_view_own_page(self):
        self.req.user = self.renter_user
        kwargs = {'request': self.req,
                  'renter': self.renter.username,
                  'year': self.today.year,
                  'month': self.today.month,
                  'day': self.today.day}
        response = renter_detail(**kwargs)
        self.assertEqual(response.status_code, 200)        

    def test_renter_should_not_be_able_to_view_other_renter_page(self):
        self.req.user = self.renter_user
        kwargs = {'request': self.req,
                  'renter': self.renter2.username,
                  'year': self.today.year,
                  'month': self.today.month,
                  'day': self.today.day}
        self.assertRaises(PermissionDenied, renter_detail, **kwargs)

    def test_renter_should_not_be_able_to_view_day_past_account_expiration_date(self):
        self.req.user = self.renter_user
        kwargs = {'request': self.req,
                  'renter': self.renter.username,
                  'year': self.three_months_from_now.year,
                  'month': self.three_months_from_now.month,
                  'day': self.three_months_from_now.day,}
        response = renter_detail(**kwargs)
        self.assertEqual(response.status_code, 302)

    def test_super_renter_should_be_able_to_view_any_day_for_renter_past_renter_account_expiration_date(self):
        self.req.user = self.superuser
        kwargs = {'request': self.req,
                  'renter': self.renter.username,
                  'year': self.three_months_from_now.year,
                  'month': self.three_months_from_now.month,
                  'day': self.three_months_from_now.day}
        response = renter_detail(**kwargs)
        self.assertEqual(response.status_code, 200)

    def anonymous_user_should_not_be_able_to_view_renter_account(self):
        kwargs = {'request': self.req,
                  'renter': self.renter.username}
        self.assertRaises(PermissionDenied, renter_account, **kwargs)

    def test_renter_should_be_able_to_view_own_account(self):
        self.req.user = self.renter_user
        kwargs = {'request': self.req,
                  'renter': self.renter.username}
        response = renter_account(**kwargs)
        self.assertEqual(response.status_code, 200)

    def test_renter_should_not_be_able_to_view_other_renter_account(self):
        self.req.user = self.renter_user
        kwargs = {'request': self.req,
                  'renter': self.renter2.username}
        self.assertRaises(PermissionDenied, renter_account, **kwargs)

    def test_super_renter_should_be_able_to_view_other_renter_account(self):
        self.req.user = self.superuser
        kwargs = {'request': self.req,
                  'renter': self.renter.username}
        response = renter_account(**kwargs)
        self.assertEqual(response.status_code, 200)

    # def test_changes_to_account_post_properly(self):
    #     pass
    
    # def test_anonymous_user_should_not_be_able_to_change_renter_account(self):
    #     pass

    # def test_renter_should_be_able_to_change_own_account(self):
    #     pass

    # def test_renter_should_not_be_able_to_change_other_renter_account(self):
    #     pass

    # def test_super_renter_should_be_able_to_change_other_renter_account(self:
    #     pass

    #Reserving and unreserving

    # def test_flexible_renter_should_be_able_to_reserve_time_slot_in_future_if_time_slot_not_fixed(self):
    #     pass

    # def test_flexible_renter_should_be_able_to_unreserve_time_slot_in_future_if_time_slot_not_fixed(self):
    #     pass

    # def test_flexible_renter_should_not_be_able_to_unreserve_own_time_slot_in_future_unless_less_than_a_certain_amount_of_time_has_passed(self):
    #     pass

    # def test_flexible_renter_should_not_be_able_to_unreserve_own_time_slot_in_future_if_time_slot_fixed(self):
    #     pass

    # def test_super_renter_should_be_able_to_unreserve_time_slot_in_future_even_if_time_slot_fixed(self):
    #     pass

    # def test_unreserving_fixed_time_slot_should_set_can_be_changed_on_time_slot_to_true(self):
    #     pass

    # def test_renter_should_not_be_able_to_unreserve_timeslot_a_certain_number_of_hours_before_timeslot_starts_unless_within_grace_period(self):
    #     pass

    # def test_flexible_renter_should_not_be_able_to_reserve_other_renter_time_slot(self):
    #     pass

    # def test_flexible_renter_should_not_be_able_to_unreserve_other_renter_time_slot(self):
    #     pass

    # def test_fixed_renter_should_not_be_able_to_reserve_time_slot(self):
    #     pass

    # def test_fixed_renter_should_not_be_able_to_unreserve_time_slot(self):
    #     pass

    # def test_super_renter_should_be_able_to_reserve_other_renter_time_slot(self):
    #     pass

    # def test_super_renter_should_be_able_to_unreserve_other_renter_time_slot(self):
    #     pass

    # def test_super_renter_should_be_able_to_reserve_time_slot_in_past(self):
    #     pass

    # def test_super_renter_should_be_able_to_unreserve_time_slot_in_past(self):
    #     pass

    # def test_super_user_reserving_time_slot_for_renter_sets_reserved_on_time_slot_to_true(self):
    #     pass

    # def test_renter_reserving_time_slot_for_renter_sets_reserved_to_true_on_time_slot(self):
    #     pass


    # Time slot history

    # def test_super_renter_reserving_time_slot_for_self_records_history_as_for_self_and_by_self(self):
    #     pass

    # def test_super_renter_reserving_time_slot_for_renter_records_history_as_for_renter_and_by_super_renter(self):
    #     pass

    # def test_renter_reserving_time_slot_for_renter_records_history_as_for_renter_and_by_renter(self):
    #     pass

    # def test_super_renter_unreserving_time_slot_for_self_records_history_as_for_self_and_by_self(self):
    #     pass

    # def test_super_renter_unreserving_time_slot_for_renter_records_history_as_for_renter_and_by_super_renter(self):
    #     pass

    # def test_renter_unreserving_time_slot_for_renter_records_history_as_for_renter_and_by_renter(self):
    #     pass

    # Available Credits
    # def testAvailableCreditsForRenterShouldBeOneLessAfterReservingTimeSlot(self):
    #     pass
    
    # def testAvailableCreditsForRenterShouldBeOneMoreAfterUnReservingTimeSlot(self):
    #     pass

    # def testRenterShouldNotBeAbleToReserveTimeSlotWhenAvailableCreditsAreZero(self):
    #     pass

    #Accounts

    # def testRenterShouldNotBeAbleToChangeOtherRenterAccount(self):
    #     pass

    # def testSuperUserShouldBeAbleToChangeOtherRenterAccount(self):
    #     pass

    # Extras

    # def testDeletingRenterShouldNotDeleteAssociatedTimeSlots(self):
    #     pass
