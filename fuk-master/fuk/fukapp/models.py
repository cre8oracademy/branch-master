from django.db import models
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from datetime import date
from fukapp.managers import ShoppingItemManager
# Create your models here.



class Competition(models.Model):
  """A fuk competition."""
  EG_CHOICES=(
   ('E', 'Everyone'),
   ('G', 'Goldens Only'),
   )
  title = models.CharField(max_length=128, help_text="Competition title, as displayed on site")
  comp_id = models.CharField(max_length=128, help_text="Choose an ID for this competition, for internal use", unique=True)
  slug = models.SlugField(help_text="URL slug for competition")
  teaser = models.TextField(help_text="HTML to appear on the competitions listing page")
  teaser_image = models.ImageField(upload_to="img/compteasers", help_text="This image is not automatically resized.")
  promoter = models.CharField(max_length=64, help_text="Competition promoter")
  eligibility = models.CharField(max_length=1, choices= EG_CHOICES, default='E')
  body = models.TextField(help_text="Body text of the competition page")
  start_date = models.DateField()
  end_date = models.DateField()
  terms = models.TextField(help_text='Enter terms and conditions, one per line.', blank=True)
  collect_emails = models.BooleanField(default=False, help_text="Whether to request email addresses from entrants")
  published = models.BooleanField(default=False, help_text="Make competition live in listing. It will still be visible at its URL for approval etc")
  entry_count = models.IntegerField(default=0)
  
  def __unicode__(self):
    return self.comp_id
    
  def is_live(self):
    """Return true if the competition is live (determined by start and end dates and published status.)"""
    if not self.published:
      return False
    today = date.today()
    if self.start_date <= today and self.end_date >= today:
      return True
    else:
      return False
    
  def user_has_entered(self, user):
    """ Return true  if a specified user has entered this comp. """
    entry = Competition.objects.filter(competitionentry__user=user, competitionentry__competition=self)
    try:
      entry.get()
      return True
    except Competition.DoesNotExist:
      return False

  def winners(self):
    """ Return a list of competition winners """
    wins = self.competitionentry_set.filter(winner=True)
    return wins.values_list('user__username', flat=True)
    
  def has_ended(self):
    """ This competition has finished. Used from the view to decide if we want to load winners. """
    today = date.today()
    if today > self.end_date:
      return True
    else:
      return False
      
  def user_can_enter(self, user):
    if not user.is_authenticated():
      return False
    if self.eligibility == 'G':
      # if this is an elite comp, are we elite?
      if user.get_profile().is_elite():
        return True
      else:
        return False
    return True

  def get_absolute_url(self):
    return reverse('competition_detail', kwargs = {'slug': self.slug})

            
class CompetitionEntry(models.Model):
  """A user entry for a competition."""
  user = models.ForeignKey(User)
  competition = models.ForeignKey(Competition)
  entered = models.DateTimeField(auto_now_add=True)
  winner = models.BooleanField(default=False, help_text="Tick box if this person has won.")
  mailingpref = models.BooleanField(default=False, verbose_name="Opt-in to 3rd party")
  
  class Meta:
    verbose_name_plural = "Competition entries"
    
  def __unicode__(self):
    return "%s:%s" % (self.user, self.competition)
    
  def save(self, force_insert=False, force_update=False, *args, **kwargs):
    """ Update the competition entry count when a new entry is posted. """
    if self.id is None:
      c=self.competition
      c.entry_count += 1
      c.save()
    return super(CompetitionEntry, self).save(force_insert, force_update, *args, **kwargs)
    
    
    
#Shopping section

class ShoppingItem(models.Model):
  """Single promotional item for the shopping page."""
  title = models.CharField(blank=True, max_length=255, help_text="Optional title")
  content = models.TextField(blank=False, help_text="Raw HMTL for the shopping item.")
  restricted = models.BooleanField(default=False, help_text="Tick box if this is GJ only.")
  published = models.BooleanField(default=False, help_text="Tick box to make item live.")
  sticky = models.BooleanField(default=False, help_text="Tick box to make item sticky at top of shopping page.")
  added = models.DateTimeField(blank=True, auto_now_add=True, editable=False)
  
  
  class Meta:
    ordering = ['-sticky', '-added']
    

  def __unicode__(self):
    return u"Shopping Item"

  objects = ShoppingItemManager()

class ArchiveContent(models.Model):
    """ The legacy content model. 
    Items are stored under their original node id, with the original drupal path stored in a path field (can't be used as a slug because of slashes) """
    title = models.CharField(max_length=128)
    path = models.CharField(max_length=128)
    body = models.TextField()
    ogauthor = models.ForeignKey(User, verbose_name="Original author")
    ogtype = models.CharField(max_length=64, help_text="The original content type of the story in Drupal.", verbose_name="Content type")
    pub_date = models.DateTimeField(help_text="Original publish date of this story.")
    terms = models.CharField(max_length=128)
    
    

class Affiliate(models.Model):
    """ Affiliate code substitutions. TODO add some way of doing custom subs for things like Amazon."""
    name = models.CharField(max_length=128)
    domain = models.CharField(max_length=128, help_text="The URL class to match. No http:// or www required (in case there are multiple domain prefixes), can be something like 'my-wardrobe.com'")
    linkcode = models.CharField(max_length=128, help_text="The deep link URL. Put {url} in the place that original link should go.")
    # use <url> as placeholder, as <> would be illegal characters in the actual url, so no chance of bum match
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name
        
    def sub_me(self, s, link):
        """Take the string and link, format an affiliate url and return the replaced string"""
        linkcode = 'href="%s' % self.linkcode.replace('{url}', link)
        href = 'href="%s' % link
        s = s.replace(href, linkcode)
        return s
    
    

def affiliate_replace(txt):
    """Process all affiliate links in the txt."""
    import re
    affils = Affiliate.objects.all().filter(active=True)    
    url_regex = r'href="(https?://[-A-Z0-9+&@#/%?=~_|$!:,.;]*[A-Z0-9+&@#/%=~_|$])'
    patt = re.compile(url_regex, re.I)
    urls = patt.findall(txt)
    if not urls:
        return txt    
    for a in affils:
        for u in urls:
            if u.find(a.domain) != -1:
                txt=a.sub_me(txt, u)
    return txt
            
            

    