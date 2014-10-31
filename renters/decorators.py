
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.functional import wraps


def restricted(func):
    @wraps(func)
    def decorator(request, *args, **kwargs):
        if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
            return HttpResponseRedirect('/accounts/login/')

        if request.user.is_superuser:
            return func(request, *args, **kwargs)

        renter = request.user.get_profile()
        the_date = datetime.date.today()

        if not renter.account_active:
            return HttpResponseRedirect(reverse('account_expired'))

        if the_date >= renter.account_expires:
            return HttpResponseRedirect(reverse('account_expired'))
            
        if 'renter' in kwargs.keys():
            username = kwargs['renter']
            if not renter.username == username:
                raise PermissionDenied

        if 'year' in kwargs.keys():
            year, month, day = kwargs['year'], kwargs['month'], kwargs['day']
            requested_date = datetime.date(int(year), int(month), int(day))
            if requested_date > renter.can_view_or_change_up_to:
                request.user.message_set.create(message="Sorry, you can't see that far in advance.")
                return HttpResponseRedirect(reverse('renter_index',
                                                    kwargs = {
                                                        'renter': request.user.username,
                                                        }))

        return func(request, *args, **kwargs)
    return decorator
