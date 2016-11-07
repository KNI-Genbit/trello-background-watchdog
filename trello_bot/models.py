from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from django.core.urlresolvers import reverse
from trello import TrelloApi
from pprint import pprint


@python_2_unicode_compatible
class Board(object):
    def __init__(self, resp, api=None):
        self.idBoard = resp.get('id', resp.get('idBoard'))
        self.name = resp['name']
        self.slug = resp.get('shortLink', self.idBoard)
        self.resp = resp
        self.api = api

    def __str__(self):
        return u"{name} (#{idBoard})".format(**self.__dict__)

    def get_absolute_url(self):
        return reverse('trello_bot:board_details', kwargs={'slug': self.slug})

    def get_pref(self):
        return self.api.boards.get_myPref(self.idBoard)


class Member(object):
    def __init__(self, idMember, username, api=None):
        self.idMember = idMember
        self.username = username
        self.api = api

    def __str__(self):
        return u"{username} (#{idMember})".format(**self.__dict__)


class TokenQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)


class Token(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    token = models.CharField(verbose_name=_("Name"), max_length=150)
    objects = TokenQuerySet.as_manager()

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")
        ordering = ['created', ]

    @property
    def api(self):
        return TrelloApi(apikey=settings.TRELLO_APP_KEY,
                         token=self.token)

    @cached_property
    def member(self):
        resp = self.api.members.get("me")
        return Member(idMember=resp['id'], username=resp['username'])

    @cached_property
    def board_list(self):
        return [Board(x, self.api) for x in self.api.members.get_board("me")]

    def get_board(self, board):
        return Board(self.api.boards.get(board), self.api)
