from django import forms
from principal.models import Tag



class JobMultifieldForm(forms.Form):
    keywords = forms.CharField(label='Title/Description', 
    required=False, 
    widget=forms.TextInput(attrs={'class':'form-control'}))
    
    location = forms.CharField(label='Location', 
    required=False,
    widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    salary_avalible = forms.BooleanField(label='Salary avalible', 
    required=False,
    widget=forms.CheckboxSelectMultiple(attrs={'class':'scrollbar-y'}))

class JobSkillsForm(forms.Form):
    skills = forms.ModelMultipleChoiceField(label='Skills', 
    queryset=Tag.objects.all(),
    widget=forms.CheckboxSelectMultiple())

class JobSimilar(forms.Form):
    id = forms.CharField(label='Id del trabajo', 
    required=False, 
    widget=forms.TextInput(attrs={'class':'form-control'}))