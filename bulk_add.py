
import datetime

from room_scheduler.timeslots.models import TimeSlot, TimeSlotHistory
from room_scheduler.renters.models import Renter
from django.contrib.auth.models import User


class BulkOperation(object):
    def __init__(self, start_date, end_date, times, isoweekdays):
        self.start_date = start_date
        self.end_date = end_date
        self.times = [(datetime.time(sh, sm), datetime.time(eh, em)) for ((sh, sm), (eh, em)) in times]
        self.isoweekdays = isoweekdays

    def _check_if_exists(self, start_time, end_time, date):
        try:
            t = TimeSlot.objects.get(start_time=start_time,
                                     end_time=end_time,
                                     date=date)
            print "%s already exists!" % t
            return True
        except TimeSlot.DoesNotExist:
            return False

    def _start_end_times_in_range(self):
        count = 0
        roving_date = self.start_date
        while roving_date <= self.end_date:
            if roving_date.isoweekday() not in self.isoweekdays:
                roving_date = roving_date + datetime.timedelta(1)
                continue
            for (start_time, end_time) in self.times:
                yield (start_time, end_time, roving_date)
                roving_date = roving_date + datetime.timedelta(1)
                count += 1
                if count % 10 == 0: print "."
                

    def bulk_add_timeslots(self, renter=None, can_be_changed_by_renter=False):
        for (start_time, end_time, roving_date) in self._start_end_times_in_range():
            if self._check_if_exists(start_time, end_time, roving_date):
                continue
            timeslot = TimeSlot(start_time=start_time, end_time=end_time, date=roving_date)
            if renter:
                timeslot.renter = renter
            timeslot.can_be_changed_by_renter = can_be_changed_by_renter
            timeslot.save()
        print "\nDone!"

    def bulk_remove_timeslots(self):
        for (start_time, end_time, date) in self._start_end_times_in_range():
            if self._check_if_exists(start_time, end_time, date):
                t = TimeSlot.objects.get(start_time=start_time, 
                                         end_time=end_time, 
                                         date=date)
                t.delete()
        print "\nDone!"


def add():
    start = datetime.date(2012, 1, 1)
    end = datetime.date(2012, 12, 30)
    times = [((22, 00), (11, 59))]
    isoweekdays = [1, 2, 3]
    b = BulkOperation(start, end, times, isoweekdays)
    b.bulk_add_timeslots()

def remove():
    start = datetime.date(2012, 1, 1)
    end = datetime.date(2012, 2, 29)
    times = [((21, 00), (23, 00))]
    isoweekdays = [4]
    b = BulkOperation(start, end, times, isoweekdays)
    b.bulk_remove_timeslots()

    start = datetime.date(2012, 3, 1)
    end = datetime.date(2012, 12, 31)
    times = [((20, 00), (22, 00))]
    isoweekdays = [4]
    b = BulkOperation(start, end, times, isoweekdays)
    b.bulk_remove_timeslots()


if __name__ == '__main__':
    job()
