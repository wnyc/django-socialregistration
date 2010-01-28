import urllib2
from django.conf import settings
from django.contrib.auth import logout
from django.template import RequestContext  

from socialregistration.models import FacebookProfile, TwitterProfile, HyvesProfile
from socialregistration.utils import (OAuthTwitter, OAuthHyves)

def auth(request):
    profile = None
    if request.user.is_authenticated():
        if request.session['_auth_user_backend'].endswith('FacebookAuth'):
            try:
                profile = FacebookProfile.objects.get(user=request.user)
            except FacebookProfile.DoesNotExist:
                logout(request)
        elif request.session['_auth_user_backend'].endswith('TwitterAuth'):
            try:
                profile = TwitterProfile.objects.get(user=request.user)
            except TwitterProfile.DoesNotExist:
                logout(request)
        elif request.session['_auth_user_backend'].endswith('HyvesAuth'):
            try:
                profile = HyvesProfile.objects.get(user=request.user)
            except HyvesProfile.DoesNotExist:
                logout(request)

    return {
        'request': request,
        'profile': profile,
    }
