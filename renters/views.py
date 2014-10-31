
from calendar import monthrange
import datetime

from icalendar import Calendar, Event

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response 
from django.template import RequestContext

from room_scheduler import settings 
from room_scheduler.renters.decorators import restricted
from room_scheduler.renters.forms import RenterForm
from room_scheduler.renters.models import Renter
from room_scheduler.timeslots.forms import ReservationForm
from room_scheduler.timeslots.models import TimeSlot, TimeSlotHistory
from room_scheduler.utilities.helper_functions import date_to_string, get_next_month, get_previous_month


def account_expired(request):
    return render_to_response('renters/account_expired.html',
                              context_instance=RequestContext(request),
                              )


@restricted
def renter_landing(request):
    return HttpResponseRedirect(reverse('renter_index',
                                        kwargs = {'renter': request.user.username}))


@restricted
def renter_index(request, renter):
    year, month, day = date_to_string(datetime.date.today())
    return HttpResponseRedirect(reverse('renter_detail',
                                        kwargs={'renter': renter,
                                                'year': year,
                                                'month': month,
                                                'day': day}))


@restricted
def renter_detail(request, renter, year, month, day):
    renter = get_object_or_404(User, username=renter).get_profile()
    the_date = datetime.date(int(year), int(month), int(day))
    next_month = get_next_month(int(year), int(month))
    next_next_month = get_next_month(next_month.year, next_month.month) 
    next_next_next_month = get_next_month(next_next_month.year, next_next_month.month)
    previous_month = get_previous_month(int(year), int(month))
    time_slots = TimeSlot.objects.all().filter(date=the_date).order_by('start_time')

    for time_slot in time_slots:
        can_reserve, message = time_slot.can_reserve(request.user, renter)
        if can_reserve:
            time_slot.show_can_reserve_button = True
        else:
            can_unreserve, message = time_slot.can_unreserve(request.user, renter)          
            if can_unreserve:
                time_slot.show_can_unreserve_button = True

    available_credits = renter.calculate_available_credits_for_month(month, year)

    if renter.account_expires - datetime.timedelta(30) <= datetime.date.today():
        expiration_message = "Warning!  Your account will expire on %s.\n" % (renter.account_expires.strftime("%A, %B %d, %Y"))
        request.user.message_set.create(message=expiration_message)
    
    return render_to_response(
        'renters/renter_detail.html',
        {'renter': renter,
        'the_date': the_date,
        'next_month': next_month,
        'next_next_month': next_next_month,
        'next_next_next_month': next_next_next_month,
        'previous_month': previous_month,
        'time_slots': time_slots,
        'available_credits': available_credits,},
        context_instance=RequestContext(request))


@restricted
def reserve_time_slot(request):
    if not request.method == 'POST':
        return HttpResponseRedirect('/')
    form = ReservationForm(request.POST) 
    if form.is_valid():
        renter_username = form.cleaned_data['renter_username']
        renter = User.objects.get(username=renter_username).get_profile()
        time_slot_pk = form.cleaned_data['time_slot_pk']
        time_slot = TimeSlot.objects.get(pk=time_slot_pk)

    year, month, day = date_to_string(time_slot.date)
    now = datetime.datetime.now()

    can_reserve, message = time_slot.can_reserve(request.user, renter)
    if can_reserve:
        time_slot.renter = renter
        time_slot.when_reserved = now
        time_slot.save()
        request.user.message_set.create(message=u"Success!  Reservation created for %s for a time slot from %s to %s on %s" % (
            renter.full_name,
            time_slot.start_time.strftime("%I:%M %p"),
            time_slot.end_time.strftime("%I:%M %p"),
            time_slot.date.strftime("%A, %B %d, %Y"),))

        history = TimeSlotHistory(saver=request.user.get_profile(),
                                  saved_for=renter,
                                  time_slot=time_slot)
        history.reserved = True
        history.save()

    else:
        request.user.message_set.create(message=message)
    
    return HttpResponseRedirect(reverse('renter_detail',
                                        kwargs={'renter': renter.username,
                                                'year': year,
                                                'month': month,
                                                'day': day})) 


@restricted
def unreserve_time_slot(request):
    if not request.method == 'POST':
        return HttpResponseRedirect('/')

    form = ReservationForm(request.POST) 
    if form.is_valid():
        renter_username = form.cleaned_data['renter_username']
        renter = User.objects.get(username=renter_username).get_profile()
        time_slot_pk = form.cleaned_data['time_slot_pk']
        time_slot = TimeSlot.objects.get(pk=time_slot_pk)

    year, month, day = date_to_string(time_slot.date)
    now = datetime.datetime.now()

    can_unreserve, message = time_slot.can_unreserve(request.user, renter)
    if can_unreserve:
        full_name = time_slot.renter.full_name
        start_time = time_slot.start_time.strftime("%I:%M %p") 
        end_time = time_slot.end_time.strftime("%I:%M %p")
        date = time_slot.date.strftime("%A, %B %d, %Y")

        history = TimeSlotHistory(saver=request.user.get_profile(),
                                  saved_for=time_slot.renter,
                                  time_slot=time_slot)

        time_slot.renter = None
        time_slot.when_reserved = None
        time_slot.save()

        history.reserved = False
        history.save()

        message = "Success!  The reservation held for %s from %s to %s on %s \
        has been cancelled." % (full_name, start_time, end_time, date)

    request.user.message_set.create(message=message) 

    return HttpResponseRedirect(reverse('renter_detail',
                                        kwargs={'renter': renter.username,
                                                'year': year,
                                                'month': month,
                                                'day': day})) 


@restricted
def renter_account(request, renter):
    renter = get_object_or_404(User, username=renter).get_profile()
    all_time_slots_in_future_for_renter = TimeSlot.objects.all().filter(renter=renter, date__gte=datetime.date.today())
    rental_history = TimeSlot.objects.all().filter(renter=renter, date__lt=datetime.date.today())
    month, year = str(datetime.date.today().month), str(datetime.date.today().year) 
    available_credits = renter.calculate_available_credits_for_month(month, year)
    form = RenterForm(instance=renter)

    if request.method == 'POST':
        form = RenterForm(request.POST, instance=renter)
        if form.is_valid():
            print "form is valid"
            form.save()
            request.user.message_set.create(message="Success!  You've just changed account details.  Please check them to make sure that they match what you wanted.")
        else:
            form = RenterForm(instance=renter)

    return render_to_response(
        'renters/renter_account.html',
        {'renter': renter,
         'all_time_slots_in_future_for_renter': all_time_slots_in_future_for_renter,
         'rental_history': rental_history,
         'available_credits': available_credits,
         'form': form},
        context_instance=RequestContext(request))


def _get_cal(site):
    """Hey, thanks to this dude!
    http://www.elfsternberg.com/2010/10/06/generating-ics-files-djangoevents/
    """
    cal = Calendar()
    cal.add('prodid', '-//%s Events Calendar//%s//' % (site.name, site.domain))
    cal.add('version', '2.0')
    return cal


def _get_site_token(site):
    site_token = site.domain.split('.')
    site_token.reverse()
    site_token = '.'.join(site_token)
    return site_token


@permission_required('is_superuser', login_url='/admin/')
def full_iCal_export(request):
    if not hasattr(request, 'user') and request.user.is_superuser:
        raise PermissionDenied
    site = Site.objects.get_current()
    cal = _get_cal(site)
    for timeslot in TimeSlot.objects.all_future_reservations():
       ical_event = Event()
       start = datetime.datetime(timeslot.date.year,
                                 timeslot.date.month,
                                 timeslot.date.day,
                                 timeslot.start_time.hour,
                                 timeslot.start_time.minute)
       end = datetime.datetime(timeslot.date.year,
                               timeslot.date.month,
                               timeslot.date.day,
                               timeslot.end_time.hour,
                               timeslot.end_time.minute)
       ical_event.add('summary', 'iBeam reserved for %s' % timeslot.renter)
       ical_event.add('dtstart', start)
       ical_event.add('dtend', end)
       site_token = _get_site_token(site)
       ical_event['uid'] = '%d.event.events.%s' % (timeslot.id, site_token)
       cal.add_component(ical_event)
    response = HttpResponse(cal.as_string(), mimetype="text/calendar")
    response['Content-Disposition'] = 'attachment; filename=ibeam_reservations.ics'
    return response


@restricted
def renter_iCal_export(request, renter):
    """Hey, thanks to this dude!
    http://www.elfsternberg.com/2010/10/06/generating-ics-files-djangoevents/
    """
    site = Site.objects.get_current()
    cal = _get_cal(site)
    renter = get_object_or_404(User, username=renter).get_profile()
    for timeslot in renter.future_time_slots:
       ical_event = Event()
       start = datetime.datetime(timeslot.date.year,
                                 timeslot.date.month,
                                 timeslot.date.day,
                                 timeslot.start_time.hour,
                                 timeslot.start_time.minute)
       end = datetime.datetime(timeslot.date.year,
                               timeslot.date.month,
                               timeslot.date.day,
                               timeslot.end_time.hour,
                               timeslot.end_time.minute)
       ical_event.add('summary', 'iBeam Reservation')
       ical_event.add('dtstart', start)
       ical_event.add('dtend', end)
       site_token = _get_site_token(site)
       ical_event['uid'] = '%d.event.events.%s' % (timeslot.id, site_token)
       cal.add_component(ical_event)
    response = HttpResponse(cal.as_string(), mimetype="text/calendar")
    response['Content-Disposition'] = 'attachment; filename=%s.ics' % renter.username
    return response
