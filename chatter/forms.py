

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_file_size(value):
    '''Check if the uploaded file is larger than 5 MB (5 * 1024 * 1024 bytes)'''
    max_size = 2 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError('File size must be no larger than 2 MB.')



class TwitteForm(forms.Form):
    text = forms.CharField(max_length=120,label='your idea',widget=forms.Textarea({"name":"body","sytle":"height:3em; width:400px;",'class':'editable'}),        error_messages={
            'required': 'Please enter your name.',
            'max_length': 'The twitte has exceeded 120 characters.',
        })
    publishedAt = forms.DateTimeField(label='',widget=forms.HiddenInput,initial=timezone.now())
  

    


class CreateUserForm(forms.Form):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email_address = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    user_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(label='password',max_length=50,widget=forms.PasswordInput(attrs={'placeholder': 'password'}))


class LoginUserForm(forms.Form):
    user_name = forms.CharField(label="username",max_length=30,widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(label='password',max_length=50,widget=forms.PasswordInput(attrs={'placeholder': 'password'}))



class EditProfileForm(forms.Form):
    name = forms.CharField(max_length=100)
    user_name = forms.CharField(label = 'User name',max_length=30)
    email_address = forms.EmailField()
    bio = forms.CharField(max_length=200,widget=forms.Textarea({'name':'body',"sytle":"height:3em; width:400px;"}),required=False)

class NewAvatarForm(forms.Form):
    date = forms.DateTimeField(label='',widget=forms.HiddenInput,initial=timezone.now())
    avatar = forms.ImageField(required=True, validators=[validate_file_size 
        ])





