Some notes about software and versions.

Production fuk.co.uk is using:

##Nginx

Two config files, one for live one for staging. 

##MySQL

##Gunicorn

Gunicorn wsgi server, with processes managed by Supervisord (see below).

##Memecached

##Supervisor

To run the site, login as the user the site is going to run as (either wide or django, depending on which server we are on). Run the command `supervisord -c /path/to/supervisord.conf`. This should obviously load on startup if possible. 

Once supervisor is running, you can connect to it with `supervisorctl -c /path/to/supervisord.conf`