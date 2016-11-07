# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^board-(?P<slug>[\w-]+)$', views.BoardDetailView.as_view(), name="board_details"),
   url(r'^$', views.BoardListView.as_view(), name="boards_list"),
   url(r'^~authorize$', views.AuthorizeView.as_view(), name="authorize"),

]
