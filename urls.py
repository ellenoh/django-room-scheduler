from django.conf.urls.defaults import *
from room_scheduler import settings
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
                       (r'^admin/(.*)', admin.site.root),
                       )

urlpatterns += patterns('',
                        url(r'^$', 'room_scheduler.views.front_page', name='front_page'),
                        (r'^users/', include('room_scheduler.renters.urls')),
                        (r'^renter/', include('room_scheduler.renters.urls')),
                        (r'^overview/', include('room_scheduler.overview.urls')),
                       (r'^accounts/login/$', 'django.contrib.auth.views.login'),
                        url('accounts/profile/$', 'room_scheduler.views.front_page'),
                        url(r'^logout$', 'room_scheduler.views.logout_user', name='logout'),
                        )


try:
    from local_settings import MEDIA_ROOT
    urlpatterns += patterns('',
                            (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': MEDIA_ROOT}),
                            )
except ImportError:
    pass
    

