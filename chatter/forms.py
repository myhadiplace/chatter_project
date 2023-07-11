from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_image_file_extension
from django import forms
from django.conf import settings
from django.utils import timezone



class TwitteForm(forms.Form):
    text = forms.CharField(max_length=120,label='your idea',widget=forms.Textarea({"name":"body","sytle":"height:3em; width:400px;",'class':'editable'}),error_messages={
        'max_length':'The twitte has exceeded 120 characters'
    })
    publishedAt = forms.DateTimeField(label='',widget=forms.HiddenInput,initial=timezone.now())
    images = forms.ImageField(required=False)

    


class CreateUserForm(forms.Form):
    name = forms.CharField(max_length=100)
    email_address = forms.EmailField()
    user_name = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50,widget=forms.PasswordInput)


class LoginUserForm(forms.Form):
    user_name = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50,widget=forms.PasswordInput)



class EditProfileForm(forms.Form):
    name = forms.CharField(max_length=100)
    user_name = forms.CharField(label = 'User name',max_length=30)
    email_address = forms.EmailField()
    bio = forms.CharField(max_length=200,widget=forms.Textarea({'name':'body',"sytle":"height:3em; width:400px;"}),required=False)

class NewAvatarForm(forms.Form):
    date = forms.DateTimeField(label='',widget=forms.HiddenInput,initial=timezone.now())
    avatar = forms.ImageField(required=False)


