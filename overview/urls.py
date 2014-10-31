from django.conf.urls.defaults import *

urlpatterns = patterns('room_scheduler.overview.views',
                       url(r'^$', 'overview_index', name='overview_index'),
                       url(r'^timeslots/$', 'timeslot_overview', name='timeslot_overview'),
                       url(r'^timeslots/(?P<year>\d{4})/(?P<month>\d{1})/$', 'timeslot_month_detail', name='timeslot_month_detail'),
                       url(r'^timeslots/(?P<year>\d{4})/(?P<month>\d{2})/$', 'timeslot_month_detail', name='timeslot_month_detail'),
                       url(r'^repeating-timeslots/$', 'repeating_timeslots', name='repeating_timeslots'),
                       url(r'^add-multiple-time-slots/$', 'add_multiple_time_slots', name='add_multiple_time_slots'),
                       url(r'^remove-multiple-time-slots/$', 'remove_multiple_time_slots', name='remove_multiple_time_slots'),
                       url(r'^add-renter-to-multiple-time-slots/$', 'add_renter_to_multiple_time_slots', name='add_renter_to_multiple_time_slots'),
                       url(r'^remove-renter-from-multiple-time-slots/$', 'remove_renter_from_multiple_time_slots', name='remove_renter_from_multiple_time_slots'),
                       url(r'^history/$', 'history', name='history'),
                       url(r'^delete-record/$', 'delete_rental_history_record', name='delete_rental_history_record'),
                       url(r'^export-to-csv/$', 'export_to_csv', name='export_to_csv'),
                       )

