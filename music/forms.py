from django.contrib.auth.models import User
from django import forms
from .models import Song

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	
	class Meta:
		model = User
		fields = ['username', 'password' ,'first_name', 'last_name', 'email' ]

class SongForm(forms.ModelForm):

	class Meta:
		model = Song
		fields = ['song_title','song_file']