from django.db import models
from fprofiles.models import get_user_info
from datetime import date

class ShoppingItemManager(models.Manager):
  def get_user_query_set(self, user):
    """Return the right set of objects according to the user's status"""
    qs = self.get_query_set()
    if (user.is_staff):
      return qs
    if user.is_authenticated():
      info = get_user_info(user.pk)
      if info['is_elite']:
        return qs.filter(published=True)
    return qs.filter(published=True, restricted=False)
        

# class CompetitionManager(models.Manager):
#   def live_competitions(self):
#     today = date.today()
#     qs = self.get_query_set()
    