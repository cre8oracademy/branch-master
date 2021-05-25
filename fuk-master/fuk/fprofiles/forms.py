from django.db import models
from fprofiles.models import *
from django import forms
from django.contrib.auth.models import User


class UserProfileForm(forms.ModelForm):
 
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        try:
            self.fields['email'].initial = self.instance.user.email
            # self.fields['first_name'].initial = self.instance.user.first_name
            # self.fields['last_name'].initial = self.instance.user.last_name
        except User.DoesNotExist:
            pass
     
    email = forms.EmailField(label="Email address",help_text='')
 
    class Meta:
      model = UserProfile
      exclude = ('user', 'postcount', 'lastactive', 'moderated_posts')        
    
    def clean_email(self):
        """ If we have a new email address, check that it is not in the db already"""
        umail = self.instance.user.email
        fmail = self.cleaned_data['email']
        if umail != fmail:
            try:
                ob = User.objects.get(email=fmail)
                # if ob exists, raise an error
                # TODO tidy up these exceptions
                raise forms.ValidationError("There is already an account with this email address")
            except User.MultipleObjectsReturned:
                raise forms.ValidationError("There is already an account with this email address")
            except User.DoesNotExist:
                pass
        return fmail
                
                
        
    def save(self, *args, **kwargs):
        """
        Update the primary email address on the related User object as well.
        """
        u = self.instance.user
        u.email = self.cleaned_data['email']
        u.save()
        profile = super(UserProfileForm, self).save(*args,**kwargs)
        return profile
        
        
class AvatarForm(forms.ModelForm):
    avatar = forms.ImageField(label="Choose a new avatar picture")
    class Meta:
      model = Avatar
      