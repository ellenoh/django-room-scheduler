from django.contrib.auth import logout
from django.http import HttpResponseRedirect
import datetime
from room_scheduler.utilities.helper_functions import date_to_string
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


@login_required(redirect_field_name='/')
def front_page(request):
    year, month, day = date_to_string(datetime.date.today())
    renter_username = request.user.username
    return HttpResponseRedirect(reverse('renter_detail',
                                        kwargs={'renter': renter_username,
                                                'year': year,
                                                'month': month,
                                                'day': day}))



def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")
