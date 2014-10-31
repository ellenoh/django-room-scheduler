from django.conf.urls.defaults import *

urlpatterns = patterns('room_scheduler.renters.views',
                       url(r'^$', 'renter_landing', name='renter_landing'),
                       url(r'^account_expired/$', 'account_expired', name='account_expired'),
                       url(r'^reserve_time_slot', 'reserve_time_slot', name='reserve_time_slot'),
                       url(r'^unreserve_time_slot', 'unreserve_time_slot', name='unreserve_time_slot'),

                       url(r'^(?P<renter>[-\w]+)/$', 'renter_index', name='renter_index'),
                       url(r'^(?P<renter>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'renter_detail', name='renter_detail'),
                       url(r'^(?P<renter>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{1})/(?P<day>\d{2})/$', 'renter_detail', name='renter_detail'), #Ugly hack - not restful!
                       url(r'^(?P<renter>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{1})/(?P<day>\d{1})/$', 'renter_detail', name='renter_detail'),
                       url(r'^(?P<renter>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1})/$', 'renter_detail', name='renter_detail'), #Ugly hack - not restful!
                       url(r'^(?P<renter>[-\w]+)/account/$', 'renter_account', name='renter_account'),
                       url(r'^(?P<renter>[-\w]+)/ical/$', 'renter_iCal_export', name='renter_iCal_export'),
                       url(r'^ical/all/$', 'full_iCal_export', name='full_iCal_export'),
                       )

