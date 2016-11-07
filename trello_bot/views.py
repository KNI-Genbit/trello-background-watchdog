from braces.views import FormValidMessageMixin, UserFormKwargsMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, TemplateView, DetailView
from trello import TrelloApi

from .forms import TokenForm
from .models import Token


class TrelloRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            try:
                self.token = Token.objects.for_user(self.request.user).get()
            except Token.DoesNotExist:
                messages.warning(request, 'Trello authorization is required.')
                return redirect(reverse('trello_bot:authorize'))
        return super(TrelloRequiredMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TrelloRequiredMixin, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context['member'] = self.token.member
        return context


class BoardListView(TrelloRequiredMixin, TemplateView):
    template_name = 'trello_bot/board_list.html'

    def get_context_data(self, **kwargs):
        context = super(BoardListView, self).get_context_data(**kwargs)
        context['board_list'] = self.token.board_list
        return context


class AuthorizeView(LoginRequiredMixin, FormValidMessageMixin, UserFormKwargsMixin, CreateView):
    model = Token
    form_class = TokenForm

    def get_context_data(self, **kwargs):
        context = super(AuthorizeView, self).get_context_data(**kwargs)
        context['token_url'] = (TrelloApi(apikey=settings.TRELLO_APP_KEY).
                                get_token_url("Trello watchdog"))
        return context

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)

    def get_success_url(self, *args, **kwargs):
        return reverse('trello_bot:boards_list')


class BoardDetailView(TrelloRequiredMixin, DetailView):
    template_name = "trello_bot/board_detail.html"

    def get_object(self):
        return self.token.get_board(self.kwargs['slug'])
