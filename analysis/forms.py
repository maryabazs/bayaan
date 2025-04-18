from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Person

class ProfilePictureForm(forms.ModelForm):
  class Meta:
    model = Person
    fields = ['image']


class SignUpForm(UserCreationForm):
  email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control-lg', 'placeholder':'Email Address'}))
  # first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control-lg', 'placeholder':'First Name'}))
  # last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control-lg', 'placeholder':'Last Name'}))

  class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')

  def __init__(self, *args, **kwargs):
    super(SignUpForm, self).__init__(*args, **kwargs)

    self.fields['username'].widget.attrs['class'] = 'form-control-lg'
    self.fields['username'].widget.attrs['placeholder'] = 'User Name'
    self.fields['username'].label = ''
    self.fields['username'].help_text = ''

    self.fields['password1'].widget.attrs['class'] = 'form-control-lg'
    self.fields['password1'].widget.attrs['placeholder'] = 'Password'
    self.fields['password1'].label = ''
    self.fields['password1'].help_text = ''

    self.fields['password2'].widget.attrs['class'] = 'form-control-lg'
    self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
    self.fields['password2'].label = ''
    self.fields['password2'].help_text = ''