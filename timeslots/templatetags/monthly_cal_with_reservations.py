
import calendar
import datetime

from django import template
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from room_scheduler.renters.models import Renter
from room_scheduler.timeslots.models import TimeSlot
from room_scheduler.utilities.helper_functions import date_to_string


register = template.Library()

def do_calendar_with_reservations(parser, token):
    try:
        tag_name, year, month, renter = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
              "%r tag requires two arguments. The year and month." \
              % token.split_contents()[0]
    return TemplateCalendarWithReservations(year, month, renter)


class CalendarWithReservations(calendar.HTMLCalendar):
    """This was handy:
    http://journal.uggedal.com/creating-a-flexible-monthly-calendar-in-django"""
    def __init__(self, year, month, renter_username):
        super(CalendarWithReservations, self).__init__(6)
        self.year = year
        self.month = month
        self.renter = User.objects.get(username=renter_username).get_profile()
        self.time_slots_for_month_for_renter = TimeSlot.objects.all().\
                                               filter(date__month=self.month,
                                                      date__year=self.year,
                                                      renter=self.renter)
        self.reservations = [timeslot.date for timeslot \
                             in self.time_slots_for_month_for_renter]

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month

        cssclasses= self.cssclasses[weekday]
        the_date = datetime.date(self.year, self.month, day)
        year, month, the_day = date_to_string(the_date)

        if the_date == datetime.date.today():
            cssclasses += ' today'
        
        if the_date > self.renter.account_expires:
            cssclasses += ' expired'
            return r'<td class="%s">%d</td>' % (cssclasses, day)

        link = "%s" % reverse('renter_detail', args=[self.renter.username,
                                                     year,
                                                     month,
                                                     the_day]
                                                     )

        if the_date in self.reservations:
            cssclasses += ' reserved'

        return r'<td class="%s"><a href="%s">%d</a></td>' % (cssclasses, link, day)


    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


class TemplateCalendarWithReservations(template.Node):
    def __init__(self, year, month, renter):
        self.year = template.Variable(year)
        self.month = template.Variable(month)
        self.renter = template.Variable(renter)    
        
    def render(self, context):
        try:
            self.year = self.year.resolve(context)
            self.year = int(self.year)
        except ValueError:
            self.year = int(resolve_variable(self.year, context))
        try:
            self.month = self.month.resolve(context)
            self.month = int(self.month)
        except ValueError:
            self.month = int(resolve_variable(self.month, context))
        self.renter_username = self.renter.resolve(context).username

        cal = CalendarWithReservations(self.year, self.month, self.renter_username)

        return cal.formatmonth(self.year, self.month)

register.tag('calendar_with_reservations', do_calendar_with_reservations)

