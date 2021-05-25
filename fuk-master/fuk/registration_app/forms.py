from django import forms
from registration_app import fields as reg_fields
from registration.forms import RegistrationFormUniqueEmail
from registration_app.sfs import check_sfs
from django.conf import settings




class RecaptchaRegistrationForm(RegistrationFormUniqueEmail):
  """Using the Unique Email base form from django registration. This
  checks for a unique username and email address.
  We then add our own validation using StopForumSpam.
  Our from needs a request object to do this, so we override the init
  
  """
  # recaptcha = reg_fields.ReCaptchaField()

  def __init__(self, request, *args, **kwargs):
    self.request = request
    super(RecaptchaRegistrationForm, self).__init__(*args, **kwargs)
  
  def clean(self):
    """
    Verify that the values entered into the two password fields
    match. Note that an error here will end up in
    ``non_field_errors()`` because it doesn't apply to a single
    field.
    
    Run a check on Stop Forum Spam
    
    """
    email = self.cleaned_data.get("email")
    if email and getattr(settings, "USE_STOP_FORUM_SPAM", False):
      if not check_sfs(self.request.get_host(), email):
        raise forms.ValidationError("Invalid email address")
    if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError("The two password fields didn't match.")
    return self.cleaned_data

    
  
