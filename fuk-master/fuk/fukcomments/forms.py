import time
import datetime

from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentSecurityForm
from fukcomments.models import FukComment
from django.contrib.contenttypes.models import ContentType
from django.forms.util import ErrorDict
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from django.utils.text import get_text_list

class FukCommentForm(CommentSecurityForm):
  comment = forms.CharField(label='Comment', widget=forms.Textarea,
                                  max_length=3000)
  
  def get_comment_model(self):
    return FukComment
    
  """ Copied from comment form"""
  def get_comment_object(self):
      """
      Return a new (unsaved) comment object based on the information in this
      form. Assumes that the form is already validated and will throw a
      ValueError if not.

      Does not set any of the fields that would come from a Request object
      (i.e. ``user`` or ``ip_address``).
      """
      if not self.is_valid():
          raise ValueError("get_comment_object may only be called on valid forms")

      CommentModel = self.get_comment_model()
      new = CommentModel(**self.get_comment_create_data())
      # skipping the check_for_duplicate for now.
      # new = self.check_for_duplicate_comment(new)

      return new
  def get_comment_create_data(self):
      """
      Returns the dict of data to be used to create a comment. Subclasses in
      custom comment apps that override get_comment_model can override this
      method to add extra fields onto a custom comment model.
      """
      return dict(
          content_type = ContentType.objects.get_for_model(self.target_object),
          object_pk    = force_unicode(self.target_object._get_pk_val()),
          comment      = self.cleaned_data["comment"],
          submit_date  = datetime.datetime.now(),
          site_id      = settings.SITE_ID,
          is_public    = True,
          is_removed   = False,
      )
      
  honeypot      = forms.CharField(required=False,
                                  label='If you enter anything in this field your comment will be treated as spam')

  def clean_honeypot(self):
      """Check that nothing's been entered into the honeypot."""
      value = self.cleaned_data["honeypot"]
      if value:
          raise forms.ValidationError(self.fields["honeypot"].label)
      return value