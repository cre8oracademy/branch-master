# fuk.co.uk Django source

This is a basic outline of the key features of the site. There is some more detail in the wiki pages, inside the `docs` folder. 


# Developing the site
## Requirements

Python 2.7
Django 1.4
MySQL 5.5
Nginx

## Images and static assets

1. All static files go in 'assets' dir, which is then subdivided by file type. 
 * 'bank' for static page images
 * 'css' for css
 * 'img' is for supporting stuff eg files for competitions or editorial that isn't uploaded directly.
 * 'js' for javascript
 * 'uni_form' is for the form style package we use - [django-crispy-forms](https://github.com/maraujop/django-crispy-forms)

2. To reference those files in a template, use the tag `{{ STATIC_URL }}`. It adds a trailing slash for you, eg `{{ STATIC_URL }}bank/myimage.png`

If you are embedding files in a non-template piece of content, for instance in a competition description, you will need to add the whole URL, which is '/static/img/yourfilename.jpg'. This slightly defeats the purpose of Django's static file handling, which is supposed to make it easy to move your files around and have the URLs update automatically, but for this type of content it shouldn't be a problem.

### Service configuration templates

The top level directory `templates` holds a number of template files for configuring various services such as Gunicorn and nginx. This is *not* a Django template directory.

### Project organisation on the server.

The source code is served from these locations:

Staging: /srv/www/fuk/staging/  
Production: /srv/www/fuk/live/

As each site runs in Python virtual environment, there is an additional directory `fuk-env` inside each instance which holds the Python env. This is not included in source control, and is ignored by the rsync 
scripts that copy it over.

The `wide` user on the server owns all the files. 

### Other data

In the `wide` user's home directory are various utilities and configurations for backup and data management.

Cron scripts run in `wide` user's crontab, and are responsible for:

- sending the notification emails to users (of updates to subscribed threads etc)
- performing a daily database dump to the `/home/wide/dbfulldump`. 

There is a copy of the crontab in the `templates` directory here.

The `/home/wide/media` directory is a symlink to the website media directory of user uploads.

By backing up `/home/wide` every day off the server, you have an up-to-date copy of all generated data from the site.

# Running the site

## Running on the server

Fuk uses [Gunicorn](http://gunicorn.org), nginx and MySQL to serve. The Gunicorn process is managed by [supervisor](http://supervisord.org). In turn, there is an upstart config that starts the supervisor process (and restarts if it fails). 

### Start the whole thing up

`sudo service start nufuk-[staging|live]` Choose either 'staging' or 'live' depending on which version you are running. This will start the supervisord process running as the user 'wide'.

## Running a local copy

To run a local copy, you can either install it straight in to your system python directories, or (recommended) install in to a virtualenv. To install in to a system environment, just do a 

`pip install -r requirements.txt` from the top level directory.

This will install all django and all the other libraries. 

To install in to a virtualenv.

    easy_install pip
    pip install virtualenvwrapper
    mkvirtualenv fuk-env
    pip install -r requirements.txt

Then, 

`python manage.py syncdb`
`python manage.py runserver`

## Fabric scripts

Use the [Fabric](https://www.fabfile.org/installing-1.x.html) utility to run updates to the server. 

Install Fabric with `pip install 'fabric<2.0'`

The fabfile.py has a collection of functions to manage provisioning and  deployment (do `fab -l` for the whole list), the main ones being:

To deploy to staging:

`fab staging deploy`

To deploy to production:

`fab production deploy`

To upload the live database and media to staging:

`fab staging reset_staging_server`

### SSH Keys

It's highly recommended to create a public key pair to use to access the server, and to run the fab commands, otherwise it will frequently ask for passwords. 



