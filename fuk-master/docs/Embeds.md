[Embed.ly](http://embed.ly)

We pass most of the embed stuff straight through to embed.ly, but also run some direct endpoint requests to reduce the load/dependency on embed.ly.

Eg, Photobucket
from the site
URL scheme:

http://i*.photobucket.com/albums/*
http://gi*.photobucket.com/groups/*
API Endpoint: http://photobucket.com/oembed

The API endpoint exists on all 's' subdomains as well, and redirects to the appropriate 's' for the media. Clients should be able to follow the redirects.

