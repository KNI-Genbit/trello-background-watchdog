# -*- coding: utf-8 -*-
from django import forms
from .models import Token
from braces.forms import UserKwargModelFormMixin
from atom.ext.crispy_forms.forms import SingleButtonMixin


class TokenForm(UserKwargModelFormMixin, SingleButtonMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TokenForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        return Token.objects.update_or_create(
            user=self.user,
            defaults={'token': self.cleaned_data['token']}
        )[0]

    class Meta:
        model = Token
        fields = ['token']
