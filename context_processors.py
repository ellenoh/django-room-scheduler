
try:
    from local_settings import MEDIA_URL
except ImportError:
    from private_settings import MEDIA_URL
    
from private_settings import ADMIN_MEDIA_PREFIX


globals_dict = {
    'MEDIA_URL': MEDIA_URL,
    'ADMIN_MEDIA_PREFIX': ADMIN_MEDIA_PREFIX,
    }


def globals(request):
    """
    Passes global variables to all the templates
    """
    return globals_dict

