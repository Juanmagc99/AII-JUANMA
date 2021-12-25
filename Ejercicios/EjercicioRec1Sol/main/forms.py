# -*- encoding: utf-8 -*-
from django import forms
from main.models import Libro, Puntuacion


class UserForm(forms.Form):
    id = forms.CharField(label='User ID')
    
class LibrosIdiomaForm(forms.Form):
    t = tuple((str(l.get('language')), str(l.get('language'))) for l in Libro.objects.all().values())

    idiomas = forms.voting_id = forms.ChoiceField(label='Idiomas', choices=t, required=True)