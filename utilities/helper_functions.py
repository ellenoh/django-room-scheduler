
from calendar import monthrange
import datetime

from django.template import RequestContext


def get_previous_month(year, month):
    """Takes a month and year and returns a datetime object for the
    first day of the previous month"""
    first_day_of_month = datetime.date(year, month, 1)
    last_day_of_previous_month = first_day_of_month - datetime.timedelta(1)
    first_day_of_previous_month = datetime.date(last_day_of_previous_month.year,
                                            last_day_of_previous_month.month,
                                            1)
    return first_day_of_previous_month


def get_next_month(year, month):
    """Takes a month and year and returns a datetime object for the
    first day of the next month."""
    last_day_of_month = datetime.date(year, month, monthrange(year, month)[1])
    first_day_of_next_month = last_day_of_month + datetime.timedelta(1)
    return first_day_of_next_month


def date_to_string(date):
    year, month, day = date.strftime("%Y-%m-%d").split("-")
    return year, month, day
