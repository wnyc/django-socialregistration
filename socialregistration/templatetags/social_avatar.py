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
        self.user_id = template.Variable(user_id)
        self.width = 50
        self.height = 50

    def get_hyves(self, hyves):
        """ Returns the image for Hyves """
        try:
            profile = HyvesProfile.objects.get(pk=hyves.pk)
        except:
            avatar = '%(media_url)simg/default-avatar.png' % {'media_url': settings.MEDIA_URL }
        else:
            avatar = profile.avatar

        return '<a href="%(avatar)s" title="%(title)s"><img src="%(avatar)s" /></a>' % {'avatar': avatar,
                                                                                        'title': profile.username, }
                                                                                        

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

    def get_avatar(self, user_id):
        """ Returns the avatar for the social application """
        try:
            profile = SocialProfile.objects.get(user__pk=user_id)
        except SocialProfile.DoesNotExist:
            return ''
        else:
            if profile.type.name == 'facebook profile': return self.get_facebook(profile.get_instance())
            elif profile.type.name == 'twitter profile': return self.get_twitter(profile.get_instance())
            elif profile.type.name == 'hyves profile': return self.get_hyves(profile.get_instance())
            else: return ''

    def render(self, context):
        try:
            user_id = self.user_id.resolve(context)
            return mark_safe(self.get_avatar(user_id))
        except template.VariableDoesNotExist:
            return ''

