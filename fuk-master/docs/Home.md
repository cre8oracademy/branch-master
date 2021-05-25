##Nufuk Wiki

Documentation and other stuff

- [[Design and implementation notes|Design]]
- [[Caching]]
- [[Styles]]
- [[Embeds]]
- [[Notes and Links for the future]]
- [[The Stack]]
- [[Search]]
- [[Logging]]

##NB

When doing a bare setup on a MySQL server, not all the indexes are created automatically. You can see all the indexes that should be created by running:

`django-admin.py sqlindexes <appname>`

##Servers

In development, the test version is live at http://dev.fuk.co.uk/ (hosted on our Kimsufi server, basement.widemedia.com)

The live version will go live on http://www.fuk.co.uk, with a stage site at http://beta.fuk.co.uk (both hosted on our main fuk server at Serverstream, spaceman.fuk.co.uk)

Dev.fuk.co.uk can be considered an anything goes, the beta server is more of a strict staging area for testing before a change goes live.

This could work better if each dev has their own test server? Could do some basic fab scripts to sort that?