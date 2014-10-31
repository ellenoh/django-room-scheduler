
from calendar import monthrange
import csv
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response 
from django.template import RequestContext

from room_scheduler.overview.forms import RepeatingTimeSlotCreateForm, RepeatingTimeSlotDeleteForm, RepeatingRentalCreateForm
from room_scheduler.renters.models import Renter
from room_scheduler.timeslots.forms import DeleteRentalHistoryRecordForm
from room_scheduler.timeslots.models import TimeSlot, TimeSlotHistory, check_can_add_multiple_time_slots, check_can_delete_multiple_time_slots
from room_scheduler.utilities.helper_functions import get_next_month, get_previous_month


@permission_required('is_superuser', login_url='/admin/')
def overview_index(request):
    active_fixed_renters = Renter.objects.all().filter(account_expires__gte=datetime.date.today(), flexible_renter=False)
    active_flexible_renters = Renter.objects.all().filter(account_expires__gte=datetime.date.today(), flexible_renter=True)
    inactive_renters = Renter.objects.all().filter(account_expires__lt=datetime.date.today())
    return render_to_response(
        'overview/overview_index.html',
        {'active_fixed_renters': active_fixed_renters,
         'active_flexible_renters': active_flexible_renters,
        'inactive_renters': inactive_renters,},
        context_instance=RequestContext(request))


@permission_required('is_superuser', login_url='/admin/')
def timeslot_overview(request):
    try:
        first_slot_date = TimeSlot.objects.all()[0].date
        #Django ORM doesn't support negative slices, so . . . 
        last_slot_date = TimeSlot.objects.all().order_by('-date')[0].date
        first_day_of_month_of_last_slot_date = datetime.date(last_slot_date.year,
                                                             last_slot_date.month,
                                                             1)
        roving_date = datetime.date(first_slot_date.year, first_slot_date.month, 1)
        first_days_of_months = [roving_date]
        while roving_date < first_day_of_month_of_last_slot_date:
            next_month = get_next_month(roving_date.year, roving_date.month)
            first_days_of_months.append(next_month)
            roving_date = next_month
        first_days_of_months.reverse()
    except IndexError:
        first_days_of_months = ''
    
    return render_to_response(
        'overview/timeslot_overview.html',
        {'first_days_of_months': first_days_of_months},
        context_instance=RequestContext(request))

    
@permission_required('is_superuser', login_url='/admin/')
def timeslot_month_detail(request, year, month):
    year = int(year)
    month = int(month)
    next_month = get_next_month(year, month)
    previous_month = get_previous_month(year, month)
    this_month = datetime.date(year, month, 1)
    timeslots_grouped_by_day = []
    days_in_month = monthrange(year, month)[1]    
    for day in range(1, (days_in_month+1)):
        roving_date = datetime.date(year, month, day)
        timeslots_for_day = TimeSlot.objects.all().filter(date=roving_date)
        if timeslots_for_day:
            timeslots_grouped_by_day.append(timeslots_for_day)
                                                          
    return render_to_response(
        'overview/timeslot_month_detail.html',
        {'timeslots_grouped_by_day': timeslots_grouped_by_day,
         'next_month': next_month,
         'previous_month': previous_month,
         'this_month': this_month},
        context_instance=RequestContext(request))


@permission_required('is_superuser', login_url='/admin/')
def add_multiple_time_slots(request):
    if request.method == 'POST':
        repeating_create_form = RepeatingTimeSlotCreateForm(request.POST) 
        if repeating_create_form.is_valid():
            start_date = repeating_create_form.cleaned_data['start_date']
            end_date = repeating_create_form.cleaned_data['end_date']
            start_time = repeating_create_form.cleaned_data['start_time']
            end_time = repeating_create_form.cleaned_data['end_time']
            isoweekday = repeating_create_form.cleaned_data['day_of_week']

        if not check_can_add_multiple_time_slots(start_date, end_date, start_time, end_time, isoweekday):
            request.user.message_set.create(message=u"Sorry, but at least one of the time slots that you're trying to create overlaps with an already existing time slot.")
        else:
            roving_date = start_date
            while roving_date < end_date + datetime.timedelta(1):
                if not (int(isoweekday) == roving_date.isoweekday()):
                    pass
                else:
                    new_time_slot = TimeSlot(start_time=start_time,
                                     end_time=end_time,
                                     date=roving_date)
                    new_time_slot.save()
                    request.user.message_set.create(message="%s successfully created" % new_time_slot)
                roving_date = roving_date + datetime.timedelta(1)
        

    else:
        repeating_create_form = RepeatingTimeSlotCreateForm()

    return render_to_response('overview/add_multiple_time_slots.html',
                              {'repeating_create_form': repeating_create_form,},
                              context_instance=RequestContext(request))


@permission_required('is_superuser', login_url='/admin/')
def remove_multiple_time_slots(request):
    if request.method == 'POST':
        repeating_delete_form = RepeatingTimeSlotDeleteForm(request.POST) 
        if repeating_delete_form.is_valid():
            start_date = repeating_delete_form.cleaned_data['start_date']
            end_date = repeating_delete_form.cleaned_data['end_date']
            start_time = repeating_delete_form.cleaned_data['start_time']
            end_time = repeating_delete_form.cleaned_data['end_time']
            isoweekday = repeating_delete_form.cleaned_data['day_of_week']

        if not check_can_delete_multiple_time_slots(start_date, end_date, start_time, end_time, isoweekday):
            request.user.message_set.create(message=u"Sorry, but at least one of the time slots that you're trying to delete is already reserved!  You can only delete time slots that aren't reserved.")
        else:
            roving_date = start_date
            while roving_date < end_date + datetime.timedelta(1):
                if not (int(isoweekday) == roving_date.isoweekday()):
                    pass
                else:
                    try:
                        time_slot_to_delete = TimeSlot.objects.get(start_time=start_time,
                                                       end_time=end_time,
                                                       date=roving_date)
                        new_time_slot.delete()
                        request.user.message_set.create(message="%s successfully deleted" % new_time_slot)
                    except DoesNotExist:
                        request.user.message_set.create(message="You tried to delete a time slot starting at %s and ending at %s on %s, but no such timeslot exists." % (start_time.strftime("%I:%M"), end_time.strftime("%I:%M"), roving_date.strftime("%m-%d-%Y")))
                roving_date = roving_date + datetime.timedelta(1)
        

    else:
        repeating_delete_form = RepeatingTimeSlotDeleteForm()

    return render_to_response('overview/add_multiple_time_slots.html',
                              {'repeating_delete_form': repeating_delete_form,},
                              context_instance=RequestContext(request))


@permission_required('is_superuser', login_url='/admin/')
def add_renter_to_multiple_time_slots(request):
    if request.method == 'POST':
        repeating_rental_create_form = RepeatingRentalCreateForm(request.POST) 
        if repeating_rental_create_form.is_valid():
            start_date = repeating_rental_create_form.cleaned_data['start_date']
            end_date = repeating_rental_create_form.cleaned_data['end_date']
            start_time = repeating_rental_create_form.cleaned_data['start_time']
            end_time = repeating_rental_create_form.cleaned_data['end_time']
            isoweekday = repeating_rental_create_form.cleaned_data['day_of_week']
            renter = repeating_rental_create_form.cleaned_data['renter']
            can_be_changed_by_renter = repeating_rental_create_form.cleaned_data['can_be_changed_by_renter']

            roving_date = start_date
            while roving_date < end_date + datetime.timedelta(1):
                if not (int(isoweekday) == roving_date.isoweekday()):
                    pass
                else:
                    try:
                        time_slot_to_alter = TimeSlot.objects.get(start_time=start_time,
                                                       end_time=end_time,
                                                       date=roving_date)
                        time_slot_to_alter.renter = renter
                        time_slot_to_alter.can_be_changed_by_renter = can_be_changed_by_renter
                        request.user.message_set.create(message="Reserved %s for %s" % (time_slot_to_alter, renter))
                        now = datetime.datetime.now()
                        history = TimeSlotHistory(saver=request.user.get_profile(),
                                                  saved_for=renter,
                                                  time_slot=time_slot_to_alter,
                                                  when_reserved=now,
                                                  reserved=True)
                        history.save()

                    except:
                        request.user.message_set.create(message="You tried to add a renter to a time slot starting at %s and ending at %s on %s, but no such timeslot exists." % (start_time.strftime("%I:%M"), end_time.strftime("%I:%M"), roving_date.strftime("%m-%d-%Y")))
                roving_date = roving_date + datetime.timedelta(1)
        

    else:
        repeating_rental_create_form = RepeatingRentalCreateForm() 


    return render_to_response('overview/add_renter_to_multiple_time_slots.html',
                              {'repeating_rental_create_form': repeating_rental_create_form,},
                              context_instance=RequestContext(request))


@permission_required('is_superuser', login_url='/admin/')
def remove_renter_from_multiple_time_slots(request):
    pass


@permission_required('is_superuser', login_url='/admin/')
def repeating_timeslots(request):
    return render_to_response('overview/overview_repeating_timeslots.html',
                              {},
                              context_instance=RequestContext(request))


@permission_required('is_superuser', login_url='/admin/')
def delete_rental_history_record(request):
    if request.method == 'POST':
        form = DeleteRentalHistoryRecordForm(request.POST)
        if form.is_valid():
            record_pk = form.cleaned_data['rental_history_record_pk']
            record = TimeSlotHistory.objects.get(pk=record_pk)
            record.delete()
    else:
        form = DeleteRentalHistoryRecordForm()
    return HttpResponseRedirect(reverse('history')) 


@permission_required('is_superuser', login_url='/admin/')
def history(request):

    form = DeleteRentalHistoryRecordForm()
    history = TimeSlotHistory.objects.all().order_by('-datetime_of_change')
    paginator = Paginator(history, 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        history = paginator.page(page)
    except (EmptyPage, InvalidPage):
        history = paginator.page(paginator.num_pages)

    return render_to_response(
        'overview/overview_activity.html',
        {'history': history,
         'form': form,},
        context_instance=RequestContext(request))


@permission_required('is_superuser', login_url='/admin/')
def export_to_csv(request):

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_renter_activity.csv'

    writer = csv.writer(response)
    history = TimeSlotHistory.objects.all()
    writer.writerow(['For Whom', 'By Whom', 'When', 'What'])
    for record in history:
        writer.writerow([record.saved_for.full_name,
                         record.saver.full_name,
                         record.datetime_of_change,
                         "%s to %s on %s" % (record.time_slot.start_time.strftime("%I:%M %p"),
                                             record.time_slot.end_time.strftime("%I:%M %p"),
                                             record.time_slot.date.strftime("%m-%d-%Y"))])
    return response
