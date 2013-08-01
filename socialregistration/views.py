"""
Created on 22.09.2009

@author: alen
"""
import uuid, urllib, cgi, facebook, time, re

from openid.consumer.consumer import DiscoveryFailure

from django.conf import settings
from django.core.mail import mail_admins
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.utils import simplejson

try:
    from django.views.decorators.csrf import csrf_protect
    has_csrf = True
except ImportError:
    has_csrf = False

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.sites.models import Site

from socialregistration.forms import UserForm
from socialregistration.utils import (OAuthClient, OAuthTwitter, OAuthLinkedin,
    OpenID, _https)
from socialregistration.models import FacebookProfile, TwitterProfile, HyvesProfile, LinkedinProfile, OpenIDProfile

FB_ERROR = _('We couldn\'t validate your Facebook credentials')

GENERATE_USERNAME = bool(getattr(settings, 'SOCIAL_GENERATE_USERNAME', getattr(
    settings, 'SOCIALREGISTRATION_GENERATE_USERNAME', False))) ##SOCIAL_GENERATE_USERNAME will deprecate

def _get_next(request):
    """
    Returns a url to redirect to after the login. We had problems with Safari
    on mac caching the home page after a login, which appears as if the user
    hasn't logged in.
    """
    to_return = ""
    if 'next' in request.GET:
        to_return = request.GET.get('next')
    elif 'next' in request.POST:
        to_return = request.POST.get('next')
    elif 'next' in request.session:
        next = request.session['next']
        del request.session['next']
        to_return = next
    else:
        to_return = getattr(settings, 'LOGIN_REDIRECT_URL', '/')
    tail = "DoNotCache=" + str(time.time())
    if to_return.find("DoNotCache") == -1:
        to_return += ("&" if to_return.find("?") > 0 else "?") + tail
    else:
        to_return = re.compile(r"DoNotCache=[\.\d]*").sub(tail, to_return)
    return to_return

def successful_account_link(request, profile):
    if isinstance(profile, OpenIDProfile):
        provider_login = "OpenID Login"
        for provider in ("google", "yahoo",):
            if profile.identity.find(provider) >= 0:
                provider_login = provider[0].upper() + provider[1:] + " Login"
    else:
        provider_login = profile._meta.object_name.replace("Profile", " Login")
    return render_to_response(
        "socialregistration/successful_account_link.html",
        dict(provider_login=provider_login,
             next=_get_next(request),
             username=profile.user.username),
        context_instance=RequestContext(request))


def _cleanup_session(request):
    # This originally simply deleted the session variables. We got a really
    # frustrating, difficult to reproduce bug from time to time that these
    # didn't exist any more at this point, causing a key error. I really wish
    # we'd figured out the underlying cause, but let's just go with this for
    # now and hope we never see it again.
    for key in ('socialregistration_user',
                'socialregistration_profile'):
        if key in request.session:
            del request.session[key]


def setup(request, template='socialregistration/setup.html',
    form_class=UserForm, extra_context=dict()):
    """
    Setup view to create a username & set email address after authentication
    """
    try:
        social_user = request.session['socialregistration_user']
        social_profile = request.session['socialregistration_profile']
    except KeyError:
        # The user jumped directly here somehow. Just go back home.
        return HttpResponseRedirect(_get_next(request))

    if not GENERATE_USERNAME:
        # User can pick own username
        if not request.method == "POST":
            form = form_class(social_user, social_profile)
        else:
            form = form_class(social_user, social_profile, request.POST)
            if form.is_valid():
                form.save()
                user = form.profile.authenticate()
                login(request, user)
                _cleanup_session(request)
                return HttpResponseRedirect(_get_next(request))

        extra_context.update(dict(form=form,
                                  social_type=str(type(social_profile))))

        return render_to_response(
            template,
            extra_context,
            context_instance=RequestContext(request)
        )
    else:
        # Generate user and profile
        social_user.username = str(uuid.uuid4())[:30]
        social_user.save()

        social_profile.user = social_user
        social_profile.save()

        # Authenticate and login
        user = social_profile.authenticate()
        login(request, user)

        # Clear & Redirect
        _cleanup_session(request)
        return HttpResponseRedirect(_get_next(request))

if has_csrf:
    setup = csrf_protect(setup)

def facebook_login(request):
    """ Handle the login """
    params = {}
    params['client_id'] = settings.FACEBOOK_APP_ID
    params['redirect_uri'] = request.build_absolute_uri(reverse('facebook_connect'))
    params['display'] = getattr(settings, 'FACEBOOK_DISPLAY', 'popup')
    params['scope'] = getattr(settings, 'FACEBOOK_SCOPE', '')

    url = 'https://graph.facebook.com/oauth/authorize?' + urllib.urlencode(params)

    return HttpResponseRedirect(url)

def facebook_connect(request, template='socialregistration/facebook.html',
                     extra_context=dict()):
    """
    View to handle graph connecting

    Authorize and create user if none

    """

    if request.GET.get("error_reason", "") == "user_denied":
        return HttpResponseRedirect(_get_next(request))

    cookie = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_API_KEY, settings.FACEBOOK_SECRET_KEY)
    if cookie:
        uid = cookie['uid']
        access_token = cookie['access_token']
    else:
        # if cookie does not exist
        # assume logging in normal way
        params = {}
        params["client_id"] = settings.FACEBOOK_APP_ID
        params["client_secret"] = settings.FACEBOOK_SECRET_KEY
        params["redirect_uri"] = request.build_absolute_uri(reverse("facebook_connect"))
        params["code"] = request.GET.get('code', '')

        url = "https://graph.facebook.com/oauth/access_token?"+urllib.urlencode(params)
        from cgi import parse_qs
        userdata = urllib.urlopen(url).read()
        res_parse_qs = parse_qs(userdata)

        # Could be a bot query
        if not res_parse_qs.has_key('access_token'):
            return render_to_response(template, extra_context,
                                      context_instance=RequestContext(request))

        access_token = res_parse_qs['access_token'][-1]

    graph = facebook.GraphAPI(access_token)
    user_info = graph.get_object('me')

    if request.user.is_authenticated():
        # Handling already logged in users connecting their accounts
        profiles = FacebookProfile.objects.filter(uid=user_info['id'])
        if profiles:
            profile = profiles[0]
            profile.access_token = access_token
            profile.save()
            # Ideally, there can only be one profile. Every once in a blue moon
            # someone manages to create multiple profiles for the same facebook
            # login. We still haven't figured out how as it isn't anything
            # obvious. We haven't figured out what to do about it in that case
            # either. For now, moderate manually. Here is a query to find these
            # dupes manually:
            """
            SELECT socialregistration_facebookprofile.uid, socialprofile_ptr_id
            FROM socialregistration_facebookprofile
            JOIN (SELECT COUNT(1) AS cnt, uid FROM
            socialregistration_facebookprofile GROUP BY UID) AS iq
            ON iq.uid = socialregistration_facebookprofile.uid
            WHERE iq.cnt > 1 ORDER BY socialregistration_facebookprofile.uid;
            """
            if len(profiles) > 1:
                usernames = ", ".join([p.username for p in profiles])
                subj = "Duplicate facebook profiles: %s" % usernames
                uids = ", ".join([str(p.uid) for p in profiles])
                msg = ("FacebookProfiles %s all have the same uid. Merge them "
                       "so the user won't have issues.") % uids
                mail_admins(subj, msg, fail_silently=False)
        else:
            profile = FacebookProfile.objects.create(user=request.user,
                                                     uid=user_info['id'],
                                                     username=user_info['name'],
                                                     access_token=access_token)

        return successful_account_link(request, profile)

    user = authenticate(uid=user_info['id'])

    if not user:
        request.session['socialregistration_user'] = User()
        request.session['socialregistration_profile'] = FacebookProfile(
                uid=user_info['id'],
                username=user_info['name'],
                access_token=access_token
            )
        request.session['next'] = _get_next(request)

        return HttpResponseRedirect(reverse('socialregistration_setup'))

    login(request, user)

    return HttpResponseRedirect(_get_next(request))

def logout(request, redirect_url=None):
    """
    Logs the user out of django. This is only a wrapper around
    django.contrib.auth.logout. Logging users out of Facebook for instance
    should be done like described in the developer wiki on facebook.
    http://wiki.developers.facebook.com/index.php/Connect/Authorization_Websites#Logging_Out_Users
    """
    auth_logout(request)

    url = redirect_url or getattr(settings, 'LOGOUT_REDIRECT_URL', '/')

    return HttpResponseRedirect(url)

def twitter(request, account_inactive_template='socialregistration/account_inactive.html',
    extra_context=dict()):
    """
    Actually setup/login an account relating to a twitter user after the oauth
    process is finished successfully
    """
    client = OAuthTwitter(
        request, settings.TWITTER_CONSUMER_KEY,
        settings.TWITTER_CONSUMER_SECRET_KEY,
        settings.TWITTER_REQUEST_TOKEN_URL,
    )

    if not client.get_access_token_or_none():
        return HttpResponseRedirect(_get_next(request))

    user_info = client.get_user_info()

    if request.user.is_authenticated():
        # Handling already logged in users connecting their accounts
        try:
            profile = TwitterProfile.objects.get(twitter_id=user_info['id'])
        except TwitterProfile.DoesNotExist: # There can only be one profile!
            profile = TwitterProfile.objects.create(user=request.user,
                                                    twitter_id=user_info['id'])

        return successful_account_link(request, profile)

    user = authenticate(twitter_id=user_info['id'])

    if user is None:
        profile = TwitterProfile(twitter_id=user_info['id'],
                                 username=user_info['screen_name'])
        user = User()
        request.session['socialregistration_profile'] = profile
        request.session['socialregistration_user'] = user
        request.session['next'] = _get_next(request)
        return HttpResponseRedirect(reverse('socialregistration_setup'))

    if not user.is_active:
        return render_to_response(
            account_inactive_template,
            extra_context,
            context_instance=RequestContext(request)
        )

    login(request, user)

    return HttpResponseRedirect(_get_next(request))

def hyves(request):
    """
    Actually setup/login an account relating to a hyves user after the oauth
    process is finished successfully
    """
    user_info = {}
    if request.method == 'POST':
        user_info['id'] = request.POST.get('userid', '')
        user_info['username'] = request.POST.get('username', '')
        user_info['url'] = request.POST.get('url', '')

    if request.user.is_authenticated():
        # Handling already logged in users connecting their accounts
        try:
            profile = HyvesProfile.objects.get(hyves_id=user_info['id'])
        except HyvesProfile.DoesNotExist: # There can only be one profile!
            profile = HyvesProfile.objects.create(user=request.user,
                                                  hyves_id=user_info['id'],
                                                  username=user_info['username'],
                                                  url=user_info['url'])

        return successful_account_link(request, profile)

    user = authenticate(hyves_id=getattr(user_info, 'id', ''))

    if user is None:
        profile = HyvesProfile(hyves_id=getattr(user_info, 'id', ''),
                               username=getattr(user_info, 'username', ''),
                               url=getattr(user_info, 'url', ''),
                               )
        user = User()
        request.session['socialregistration_profile'] = profile
        request.session['socialregistration_user'] = user
        request.session['next'] = _get_next(request)
        return HttpResponseRedirect(reverse('socialregistration_setup'))
    else:
        try:
            profile = HyvesProfile.objects.get(user=user)
        except HyvesProfile.DoesNotExist:
            pass
        else:
            profile.avatar = ''
            profile.save()

    login(request, user)
    request.user.message_set.create(message=_('You have succesfully been logged in with your hyves account'))

    return HttpResponseRedirect(_get_next(request))

def linkedin(request):
    """
    Actually setup/login an account relating to a linkedin user after the oauth
    process is finished successfully
    """
    client = OAuthLinkedin(
        request, settings.LINKEDIN_CONSUMER_KEY,
        settings.LINKEDIN_CONSUMER_SECRET_KEY,
        settings.LINKEDIN_REQUEST_TOKEN_URL,
    )

    # Perhaps the user typed in this url, or logged out from this page after
    # successfully linking accounts.
    if not client.get_access_token_or_none():
        return HttpResponseRedirect(_get_next(request))

    user_info = client.get_user_info()

    if request.user.is_authenticated():
        # Handling already logged in users connecting their accounts
        try:
            profile = LinkedinProfile.objects.get(linkedin_id=user_info['id'])
        except LinkedinProfile.DoesNotExist: # There can only be one profile!
            profile = LinkedinProfile.objects.create(user=request.user,
                                                     linkedin_id=user_info['id'],
                                                     username=user_info['screen_name'])

        return successful_account_link(request, profile)

    user = authenticate(linkedin_id=user_info['id'])

    if user is None:
        profile = LinkedinProfile(linkedin_id=user_info['id'],
                               username=user_info['screen_name'],
                               )
        user = User()
        request.session['socialregistration_profile'] = profile
        request.session['socialregistration_user'] = user
        request.session['next'] = _get_next(request)
        return HttpResponseRedirect(reverse('socialregistration_setup'))

    login(request, user)
    request.user.message_set.create(message=_('You have succesfully been logged in with your linkedin account'))

    return HttpResponseRedirect(_get_next(request))

def oauth_redirect(request, consumer_key=None, secret_key=None,
    request_token_url=None, access_token_url=None, authorization_url=None,
    callback_url=None, parameters=None):
    """
    View to handle the OAuth based authentication redirect to the service provider
    """
    request.session['next'] = _get_next(request)
    client = OAuthClient(request, consumer_key, secret_key,
        request_token_url, access_token_url, authorization_url, callback_url, parameters)
    return client.get_redirect()

def oauth_callback(request, consumer_key=None, secret_key=None,
    request_token_url=None, access_token_url=None, authorization_url=None,
    callback_url=None, template='socialregistration/oauthcallback.html',
    extra_context=dict(), verifier=None, parameters=None):
    """
    View to handle final steps of OAuth based authentication where the user
    gets redirected back to from the service provider
    """
    if request.GET.get('oauth_verifier', None):
        verifier = request.GET.get('oauth_verifier')

    client = OAuthClient(request, consumer_key, secret_key, request_token_url,
        access_token_url, authorization_url, callback_url, verifier, parameters)

    extra_context.update(dict(oauth_client=client))

    if not client.is_valid():
        return render_to_response(
            template, extra_context, context_instance=RequestContext(request)
        )

    # We're redirecting to the setup view for this oauth service
    return HttpResponseRedirect(reverse(client.callback_url))

def return_to(request):
    """
    An xrds file that OpenID providers such as Yahoo! use to verify your site.
    """
    return render_to_response(
        'socialregistration/return_to.xrds',
        dict(return_to=_openid_callback_url()),
        context_instance=RequestContext(request)
    )

def openid_redirect(request):
    """
    Redirect the user to the openid provider
    """
    request.session['next'] = _get_next(request)
    request.session['openid_provider'] = request.GET.get('openid_provider')

    provider = request.GET.get('openid_provider')
    client = OpenID(
        request,
        _openid_callback_url(),
        provider
    )
    try:
        return client.get_redirect()
    except DiscoveryFailure:
        return render_to_response(
            'socialregistration/provider_failure.html',
            dict(provider=provider),
            context_instance=RequestContext(request)
        )

def _openid_callback_url():
    return 'http%s://%s%s' % (
        _https(),
        Site.objects.get_current().domain,
        reverse('openid_callback')
    )

def openid_callback(request, template='socialregistration/openid.html',
    extra_context=dict(), account_inactive_template='socialregistration/account_inactive.html'):
    """
    Catches the user when he's redirected back from the provider to our site
    """
    if request.GET.get("openid.mode", "") == "cancel":
        return HttpResponseRedirect(_get_next(request))

    client = OpenID(
        request,
        _openid_callback_url(),
        request.session.get('openid_provider')
    )

    if client.is_valid():
        identity = client.result.identity_url
        if request.user.is_authenticated():
            # Handling already logged in users just connecting their accounts
            try:
                profile = OpenIDProfile.objects.get(
                    identity=identity,
                    site=Site.objects.get_current())
            except OpenIDProfile.DoesNotExist: # There can only be one profile with the same identity
                profile = OpenIDProfile.objects.create(user=request.user,
                    identity=identity)

            return successful_account_link(request, profile)

        user = authenticate(identity=identity)
        if user is None:
            request.session['socialregistration_user'] = User()
            request.session['socialregistration_profile'] = OpenIDProfile(
                identity=identity
            )
            return HttpResponseRedirect(reverse('socialregistration_setup'))

        if not user.is_active:
            return render_to_response(
                account_inactive_template,
                extra_context,
                context_instance=RequestContext(request)
            )

        login(request, user)
        return HttpResponseRedirect(_get_next(request))

    return render_to_response(
        template,
        dict(),
        context_instance=RequestContext(request)
    )
