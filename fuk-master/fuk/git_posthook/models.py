from django.db import models
from django.conf import settings

import subprocess

"""
Trigger a site update when called from a github posthook.
Calls deploy script on server, which pulls changes from github and rsyncs
to correct location. Finally, gunicorn server is rebooted.
"""

DEPLOYCMD="sudo -u wide /usr/local/bin/fukdeploy staging"


# Create your models here.

class GitAction(models.Model):
  """ Store information about a received commit in the database."""
  created = models.DateTimeField(auto_now_add=True)
  payload = models.TextField(verbose_name="GitHub post", null=True, blank=True)
  result = models.TextField(blank=True)
  
  def save(self, force_insert=False, force_update=False, *args, **kwargs):
    # override save method, run pull on create only.
    if self.id is None:
      self.result = run_deploy_script()
    super(GitAction, self).save(force_insert, force_update, *args, **kwargs)
    

# def run_git_command(cmd="pull"):
#   # get to the working dir and run a pull (or other command)
#   basedir = getattr(settings,'SITE_ROOT')
#   runcmd = "git " + cmd
#   c = subprocess.Popen(runcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=basedir)
#   if c.wait() != 0:
#     return "Sorry, an error occurred: %s" % c.stderr.read()
#   return c.stdout.read()

def run_deploy_script():
  c = subprocess.Popen(DEPLOYCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if c.wait() != 0:
    return "Sorry, an error occurred: %s" % c.stderr.read()
  return c.stdout.read()