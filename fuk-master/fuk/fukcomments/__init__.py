from fukcomments.models import FukComment
from fukcomments.forms import FukCommentForm

def get_model():
  return FukComment
  
def get_form():
  return FukCommentForm