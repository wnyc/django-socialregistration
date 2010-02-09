import urllib2
from django.conf import settings
from django.contrib.auth import logout
from django.template import RequestContext  

from socialregistration.models import SocialProfile
from socialregistration.utils import (OAuthTwitter, OAuthHyves)

def auth(request):
    profile = None
    if request.user.is_authenticated() and request.session['_auth_user_backend'] != 'django.contrib.auth.backends.ModelBackend':
        try:
            profile = SocialProfile.objects.get(user=request.user)
        except SocialProfile.DoesNotExist:
            logout(request)

    return {
        'request': request,
        'profile': profile,
    }
