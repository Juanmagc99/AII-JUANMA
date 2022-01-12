from django import forms
from principal.models import Tag



class JobMultifieldForm(forms.Form):
    keywords = forms.CharField(label='Title/Description', required=False)
    location = forms.CharField(label='Location', required=False)
    salary_avalible = forms.BooleanField(label='Salary avalible', required=False)

class JobSkillsForm(forms.Form):
    skills = forms.ModelChoiceField(label='Skills', empty_label="-", queryset=Tag.objects.all())