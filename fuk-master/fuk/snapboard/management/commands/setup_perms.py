from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
  """Set up basic permissions on the site. This command should only need to be run once 
  when the site is initially bootstrapped. It exists because its impossible to assign
  permissions to groups in a fixture. Any changes to group names in the group fixture
  or permissions in the code will need to be reflected here."""
  help = "Set up basic permissions on the site"
  
  def handle(self, *args, **options):
    basics = self.get_group("Basics")
    # clear existing perms
    basics.permissions.clear()
    canpost = self.get_perm("Can post unmoderated")
    basics.permissions.add(canpost)
    
    #goldens
    goldens = self.get_group("Goldens")
    goldens.permissions.clear()
    goldens.permissions.add(canpost)
    
    #mods
    mods = self.get_group("Mods")
    mods.permissions.clear()
    mods.permissions.add(canpost)
    md = self.get_perm("Can moderate posts")
    mods.permissions.add(md)
    
  def get_group(self, groupname):
    try:
      gp = Group.objects.get(name=groupname)
      return gp
    except Group.DoesNotExist:
      raise CommandError("%s group does not exist" % groupname)
      
  def get_perm(self, permname):
    try:
      gp = Permission.objects.get(name=permname)
      return gp
    except Permission.DoesNotExist:
      raise CommandError("%s permission does not exist" % permname)