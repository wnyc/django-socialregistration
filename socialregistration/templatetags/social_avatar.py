from django import template
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.conf import settings

from socialregistration.models import FacebookProfile, TwitterProfile, HyvesProfile, SocialProfile

import urllib2
from time import time

register = template.Library()

@register.tag
def social_avatar(parser, token):
    """ Returns a ``img`` tag or on facebook tag """
    try:
        tag_name, user_id = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, '%s is used as "{% social_avatar <user id> %}"' % token.contents.split()[0]
    return GetAvatar(user_id)

class GetAvatar(template.Node):
    def __init__(self, user_id, width=50, height=50):
        self.user_id = user_id
        self.width = 50
        self.height = 50

    def get_hyves(self, hyves):
        """ Returns the image for Hyves """
        d = {'hyves_token_url': settings.HYVES_REQUEST_TOKEN_URL,
             'oauth_key': settings.HYVES_CONSUMER_KEY,
             'timestamp': str(time()).split('.')[0],
             'username': hyves.username}
        url = '%(hyves_token_url)s?ha_fancylayout=False&ha_format=json&ha_method=users.getByUsername&ha_responsfields=profilepicture&ha_version=2.0&oauth_consumer_key=%(oauth_key)s&oauth_nonce=&oauth_signature_method=HMAC-SHA1&oauth_timestamp=%(timestamp)s&oauth_token=&oauth_version=1.0&username=%(username)s&oauth_signature=' % d
        return url

    def get_twitter(self, twitter):
        """ Returns the image for Twitter """
        site = urllib2.urlopen('http://twitter.com/users/%(uid)s.json' % {'uid': twitter.twitter_id,})
        json = simplejson.loads(site.read())
        d = {'image': json['profile_image_url'],
             'username': twitter.username,
             'title': _('Visit %s\'s Twitter profile' % twitter.username)}

        return '<a href="http://twitter.com/%(username)s" title="%(title)s"><img src="%(image)s" /></a>' % d

    def get_facebook(self, facebook):
        return '<fb:profile-pic uid=%(uid)s size=square facebook-logo=true />' % \
                {'uid': facebook.uid,
                 'width': self.width,
                 'height': self.height}

    def get_avatar(self):
        """ Returns the avatar for the social application """
        try:
            profile = SocialProfile.objects.get(user__pk=self.user_id)
        except SocialProfile.DoesNotExist:
            return ''
        else:
            if profile.type.name == 'facebook profile': return self.get_facebook(profile.get_instance())
            elif profile.type.name == 'twitter profile': return self.get_twitter(profile.get_instance())
            elif profile.type.name == 'hyves profile': return self.get_hyves(profile.get_instance())
            else: return ''

    def render(self, context):
        return mark_safe(self.get_avatar())
