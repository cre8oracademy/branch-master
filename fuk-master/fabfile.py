
""" 
Fabfile for deploying fuk.co.uk.
Hosts are specified as individual tasks, which are currently 

dev, staging, production or vagrant. 

All commands should be invoked with one of these options preceeding

EG `fab dev deploy` to deploy the site to the development server.

To use a predefined ssh key, add the command line arguement

eg # specify key file name on command line 
# env.key_filename = '/Users/ben/.ssh/wide-spaceman'
`fab -i /Users/ben/.ssh/wide-spaceman dev deploy

Up and running on a Vagrant virtual box
========================

There is a vagrant provisioning setup in the 'vagrant' directory of this project.
With Vagrant/Virtualbox installed, run a `vagrant up` and the provision script
will install all the server pieces needed. With a couple of tweaks, the same script
could be used to set up a live server.

Once a server is provisioned, run
`fab vagrant boostrap` to set up all the site specific config and copy the code over.

Then, running `sudo service nufuk-{environment} start', where environment is the
value of env.environment will bring up the site. Currently this command needs to
be run on the virtual server command line, there is no fab equivalent.

Running on a server
============

On a real server, the procedure is very similar. Assuming all the bits outlined in the 
provisioning.sh script are installed, a `fab {environment} bootstrap` will set up 
the site.

There are environment configs for dev, production and staging. 

Monitoring, tweaking
=============

There are a couple of fab commands for checking the log file outputs. 
`fab {environment} tailgun` will show the gunicorn server logfile, and 
`fab {environment} tailnginx` will show the file for nginx.

When making a code change, issue `fab {environment} deploy` and the code
will be uploaded and the server restarted automatically.

"""

import os, sys

from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib import files, console, django
from fabric import utils
from fabric.decorators import hosts

# from cuisine import *



RSYNC_EXCLUDE = (
		'.DS_Store',
		'.git',
		'.hg',
		'*.pyc',
		'*.example',
		'*.db',
		'media',
		'local_settings.py',
		'fabfile.py',
		'bootstrap.py',
		'gunicorn.sh',
		'*.templ', # don't upload template files
		'logs',
		'conf',
		'static',
		'vagrant'

		)

# password protection added to nginx conf unless overridden
env.pwprotect = """
				auth_basic			"Development Server";
				auth_basic_user_file /etc/nginx/htusers;
"""
env.project = 'fuk'
env.deploy = 'rsync'
env.mysql_root_pw = "nUt6oyb2uNk" # override MySQL root password as necessary
# local_code has an a trailing slash to the directory for use with rsync
env.local_code=os.path.dirname(os.path.realpath(__file__))+'/'

def _setup_path():
		# env.home = '/home/' + env.user
		env.home = '/srv/www/' + env.project
		env.root = os.path.join(env.home, env.environment)
		env.code_root = os.path.join(env.root, env.project)
		env.virtualenv_root = os.path.join(env.root, env.project+'-env')
		env.settings = 'settings.%(environment)s' % env

def spaceman():
		""" spaceman server """
		env.user = 'wide'
		env.environment = 'staging'
		env.hosts = ['spaceman.fuk.co.uk:2222']
		env.hostname = 'beta.fuk.co.uk'
		env.dbpw = 'Pz{LTZ77Ws*NXB'
		env.wsgi_server = 'gunicorn'
		env.wsgi_port = 8001
		_setup_path()



def staging():
		""" use staging environment on remote host"""
		env.user = 'wide'
		env.environment = 'staging'
		env.hosts = ['electra.fuk.co.uk:2222']
		env.hostname = 'electra.fuk.co.uk'
		env.dbpw = 'Pz{LTZ77Ws*NXB'
		env.wsgi_server = 'gunicorn'
		env.wsgi_port = 8001
		_setup_path()

def dev():
		""" testing environment on basement """
		env.user = 'wide'
		env.environment = 'dev'
		env.mysql_root_pw = 'happy days'
		env.hosts = ['basement.widemedia.com:2222']
		env.hostname = 'dev.fuk.co.uk'
		env.dbpw = 'Pz{LTZ77Ws*NXB'
		env.wsgi_server = 'gunicorn'
		env.deploy = 'rsync'
		env.wsgi_port = 8000
		_setup_path()

def vagrant():
		""" Vagrant server on localhost """
		env.hosts = ['127.0.0.1:2222']
		env.user = 'vagrant'
		env.environment = 'dev_vagrant'
		env.dbpw = 'Pz{LTZ77Ws*NXB'
		env.hostname = 'nufuk.dev' 
		env.key_filename = '/Users/ben/.vagrant.d/insecure_private_key'
		# Only use this on localhost!
		env.disable_known_hosts = True
		env.wsgi_server = 'gunicorn'
		env.wsgi_port = 8000
		_setup_path()
		
# def local():
#			""" Local testing environment"""

def production():
		""" use production environment on remote host"""
		env.user = 'wide'
		env.environment = 'production'
		env.hosts = ['electra.fuk.co.uk:2222']
		env.hostname = 'www.fuk.co.uk'
		env.dbpw = 'Pz{LTZ77Ws*NXB'
		env.wsgi_server = 'gunicorn'
		env.wsgi_port = 8000
		env.pwprotect = ''
		_setup_path()


# def print_settings():
#			require('root')
#			from django.conf import settings
#			print settings.DATABASES
#			



# def provision():
#			""" base pieces we need on this server. This function should only
#			need to be run once for a server, subsequent installs on the server
#			will need bootstrap()"""
#			require('root')
#			package_update()
#			package_ensure('build-essential')
#			package_ensure('nginx')
#			package_ensure('git-core')
#			package_ensure('curl')
#			package_ensure('mysql-server')
#			package_ensure('python-dev')
#			package_ensure('python-setuptools')
#			package_ensure('python-imaging')
#			package_ensure('libmysqlclient15-dev')
#			sudo('easy_install pip')
#			sudo('pip install virtualenv')
#			sudo('pip install supervisor')


def bootstrap():
		""" initialize remote host environment (virtualenv, deploy, update) """
		require('root')
		sudo('mkdir -p %(root)s' % env)
		sudo('mkdir -p %(root)s/logs' % env)
		sudo('mkdir -p %(root)s/conf' % env)
		sudo('mkdir -p %(root)s/media/smileys' % env)
		sudo('mkdir -p %(root)s/static' % env)
		# sudo('mkdir -p %s' % os.path.join(env.home, 'www', 'log'))
		# grant our web user owenership of the dirs
		sudo('chown -R %(user)s:%(user)s %(root)s' % env)
		
		create_virtualenv()
		update_code()
		update_requirements()
		vcmd('pip install mysql-python')
		update_nginx_conf()
		update_gunicorn_conf()
		update_upstart_conf()
		update_supervisor_conf()
		vcmd('django-admin.py collectstatic --noinput')
		upload_smilies()
		create_db()
		initial_database_sync()
		vcmd("django-admin.py setup_perms")


 

def upload_smilies():
		""" do an initial upload of our smilies data. We only run this on 
		bootstrap, as they can be uploaded directly after that."""
		require('root')
		dest = os.path.join(env.root, 'media/smileys/')
		src = 'media/smileys/*'
		put(src, dest)



		
		
def create_virtualenv():
		""" setup virtualenv on remote host """
		require('virtualenv_root')
		# args = '--clear --distribute'
		args= ''
		run('virtualenv %s %s' % (args, env.virtualenv_root))
		# add some paths to the virtualenv activation script.
		#### FIXME! these only work with virtualenvwrapper
		#### install it, or just create the env vars when using.
		pt1 = "export DJANGO_SETTINGS_MODULE=settings.%s" % (env.environment,)
		pt2 = "export PYTHONPATH=%s" % (env.code_root,)
		run('echo "%s" >> %s/bin/postactivate' % (pt1+"\n"+pt2, env.virtualenv_root))


def create_db():
		""" Create a mysql database and user if they do not exist already"""
		dbname = "fuk_%(environment)s" % env
		with settings(warn_only=True):
				result = run("echo 'SHOW DATABASES;' | mysql -u root --password=\"%s\" | grep '%s'" % (env.mysql_root_pw, dbname))
		if result.failed:
				CREATE_DB="CREATE DATABASE %s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;" % (dbname,)
				CREATE_DB+="GRANT ALL PRIVILEGES ON %s.* TO django@localhost IDENTIFIED BY '%s';" % (dbname, env.dbpw);
				run('mysql -u root --password=\"%s\" -e "%s"' % (env.mysql_root_pw, CREATE_DB))
		
def migrate():
		""" Do a South migration"""
		vcmd("django-admin.py migrate")
		

def initial_database_sync():
		""" Run a syncdb, then a migrate """
		vcmd("django-admin.py syncdb")
		migrate()


def update_code():
		""" Deploy code. Wrapper function depending on what 
		deployment method you want to use."""
		if env.deploy == 'git':
				git_deploy()
		else:
				rsync_code()
		
def backup_database():
		""" Take a dump from the database """
		# This is just stubbed out until I can find a way of accessing our database
		# settings for the site config in question. Fabric's built-in support doesn't 
		# work for non-local environments, and it's trickier still with our settings 
		# directory layout.
		# print vcmd("python -c 'from django.conf import settings;print settings.DATABASES'")

def sync_staging_db():
		""" Load most recent backup of db from server to staging environment"""
		require('root')
		if env.environment=="production":
				utils.abort("This command can only be run from staging environment")
		if not console.confirm('All data on the staging server will be replaced with data from the live server. Continue?',	default=False):
				utils.abort('Data sync aborted.')

		backup_base = "/home/wide/dbfulldump/fuk_production" 
		with cd (backup_base):
				s = run("ls -1t | head -1")
				dpath = os.path.join(backup_base, s.strip(), "fuk_production") 
		with cd (dpath):
				run("load-db.sh %s %s %s" % ("fuk_staging", "django", env.dbpw)) # hard coding Db to avoid fuck ups

def sync_staging_media():
		""" Sync the media dir on the staging server with the live media dir."""
		require('root')
		if env.environment=="production":
				utils.abort("This command can only be run from staging environment")
		# hard code remote source to avoid fuckups
		src = "/srv/www/fuk/production/media/"
		dst = "/srv/www/fuk/staging/media/"
		run("rsync -av %s %s" % (src, dst))
		
def reset_staging_server():
		""" Reset all data and media on the staging server with that from the live server."""
		sync_staging_db()
		sync_staging_media()

def rsync_code():
		""" rsync code to remote host """
		require('root', provided_by=('staging', 'production'))

		# defaults rsync options:
		# -pthrvz
		# -p preserve permissions
		# -t preserve times
		# -h output numbers in a human-readable format
		# -r recurse into directories
		# -v increase verbosity
		# -z compress file data during the transfer
		# don't transfer or wipe the virtualenv, which is in the root transfer dir on the server.
		excludes = RSYNC_EXCLUDE+(env.project+'-env',)
		extra_opts = '--omit-dir-times'
		rsync_project(
				env.root,
				env.local_code,
				exclude=excludes,
				delete=True,
				extra_opts=extra_opts,
		)

def collect_static():
	vcmd('django-admin.py collectstatic --noinput')

def reload_wsgi():
		if env.wsgi_server == 'gunicorn':
				restart_gunicorn()
		elif env.wsgi_server == 'mod_wsgi':
				touch()

def deploy():
		""" Transfer code and restart"""
		require('root')
		if env.environment == 'production':
				if not console.confirm('Are you sure you want to deploy production?',
															 default=False):
						utils.abort('Production deployment aborted.')
		update_code()
		# collect static files
		collect_static()
		reload_wsgi()

def safe_deploy():
		""" Download media and templates before deploying code."""
		reset_local_media()
		reset_local_templates()
		deploy()


def git_deploy():
		""" Deploy code with a git pull on the server. Note, this will not work if any files on the 
		server have been modified, eg via rsync. It needs a git reset --hard HEAD in that case. """
		require('root', provided_by=('dev', 'staging', 'production'))
		with cd(env.root):
				run('git pull')
				

def update_requirements():
		""" update external dependencies on remote host """
		require('root', provided_by=('staging', 'production'))
		#requirements = os.path.join(env.code_root, 'requirements')
		with cd(env.root):
				cmd = ['%(virtualenv_root)s/bin/pip install' % env]
				cmd += ['--requirement %s' % 'requirements.txt']
				run(' '.join(cmd))


def restart_gunicorn():
		""" Restart gunicorn server in supervisorctl """
		run('supervisorctl -c %s/conf/supervisord.conf restart fuk_%s' % (env.root, env.environment))


def reset_local_media():
		""" Reset local media from remote host"""
		require('root')
		media = os.path.join(env.root, 'media')
		local('rsync -rvaz %s@%s:%s .' % (env.user, env.hosts[0], media))

def sync_media():
		""" Sync live media to staging """
		
		
		
def reset_local_templates():
		""" Reset local templates from remote host. Confirm all local changes committed first"""
		require('root')
		if not console.confirm("Have you committed all local changes?", default=False):
				utils.abort('Please commit changes and try again.')
		templates = os.path.join(env.code_root, 'templates')
		local('rsync -rvaz %s@%s:%s fuk/' % (env.user, env.hosts[0], templates))
		
		
def update_nginx_conf():
		""" Use Fabric's upload_template command to do the nginx config"""
		require('root')
		# use the staging conf file if there is not a custom one for this env.
		default_template = 'staging'
		template_name = 'nginx.%s.conf' % env.environment
		if not os.path.exists(os.path.join(env.local_code, 'templates', template_name)):
			template_name = 'nginx.%s.conf' % default_template
		templ = os.path.join(env.local_code, 'templates', template_name)
		files.upload_template(templ, '/etc/nginx/sites-available/' + env.hostname, env, use_sudo=True)
		if not files.exists('/etc/nginx/sites-enabled/' + env.hostname):
				sudo('ln -s /etc/nginx/sites-available/%(hostname)s /etc/nginx/sites-enabled/%(hostname)s' % env)
		restart_nginx()
		
def enable_maintenance():
		""" Put the whole site in to maintenance mode """
		require('root')
		cfg = "/etc/nginx/sites-available/%(hostname)s" % env
		regex = "return 503;"
		files.uncomment(cfg, regex, use_sudo=True)
		restart_nginx()

def disable_maintenance():
		""" Disable whole site maintenance mode """
		require('root')
		cfg = "/etc/nginx/sites-available/%(hostname)s" % env
		regex = "return 503;"
		files.comment(cfg, regex, use_sudo=True)
		restart_nginx()
		
		
def restart_nginx():
		"""Restart the nginx server """
		require('root')
		sudo('/etc/init.d/nginx restart')

def start_supervisor():
		""" Run the upstart job that starts the supervisor daemon. 
		Only necessary when installing for first time, as you can control 
		gunicorn directly thereafter"""
		require('root')
		sudo('service nufuk-%s start' % env.environment)		
		
def update_supervisor_conf():
		""" Install a supervisor config file """
		require('root')
		conf_file = os.path.join(env.local_code, 'templates', 'supervisord.conf')
		dest = env.root + '/conf/supervisord.conf'	
		files.upload_template(conf_file, dest, env, backup=False)


def update_gunicorn_conf():
		"""Install a gunicorn config shell script"""
		require('root')
		ctx={'debug': True}
		if env.environment == 'production':
				ctx['debug'] = False
		env.update(ctx)
		templ = os.path.join(env.local_code, 'templates', 'gunicorn.sh')
		dest = os.path.join(env.root, "gunicorn.sh")
		files.upload_template(templ, dest, env)
		run('chmod 755 %s' % dest)
				
				
def update_upstart_conf():
		""" Update and install upstart conf"""
		require('root')
		dest = '/etc/init/nufuk-%s.conf' % env.environment
		templ = os.path.join(env.local_code, 'templates', 'upstart.conf')
		files.upload_template(templ, dest, env, use_sudo=True)
		sudo('chown root:root %s' % dest)
		

def tailgun(follow=''):
		""" Tail the gunicorn log file """
		lf = 'fuk_gunicorn.log'
		taillog(lf, follow)

def tailnginx(follow=''):
		""" Tail the nginx log file"""
		lf = 'nginx.access.log'
		taillog(lf, follow)


def taillog(logfile, follow):
		require('root')
		with cd(os.path.join(env.root, 'logs')):
				if follow:
						run('tail -f '+logfile)
				else:
						run('tail '+logfile)
						
						
def import_legacy(cmd=""):
		""" Migrate all the old content. """
		# get the various file paths
		if not hasattr(env, 'dpath'):
				sys.stdout.write("Enter the path to the DB files for import: ")
				env.dbpath = raw_input().strip()
		if not hasattr(env, 'avpath'):
				sys.stdout.write("Enter the path to the avatar files: ")
				env.avpath = raw_input().strip()
		with cd(env.code_root):
				with shell_env(DJANGO_SETTINGS_MODULE=env.settings):
						vcmd("python import_legacy.py -a %s -d %s" % (env.avpath, env.dbpath))
		
		

############## Utilities and helpers


def vcmd(cmd=""):
		'''Run a virtualenv-based command in the site directory.	Usable from other commands or the CLI.'''
		require('code_root')
		require('virtualenv_root')

		if not cmd:
				sys.stdout.write("Command to run: %s/bin/" % env.virtualenv_root.rstrip('/'))
				cmd = raw_input().strip()

		if cmd:
				if "django-admin.py" in cmd:
						cmd = cmd + " --settings=%s --pythonpath=%s" % (env.settings, env.code_root)
				with cd(env.code_root):
						run(env.virtualenv_root.rstrip('/') + '/bin/' + cmd)
		
