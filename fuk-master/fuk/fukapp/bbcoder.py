# -*- coding: utf-8 -*-
# Setup bbcode options

# Using the Python bbcode project https://pypi.python.org/pypi/bbcode/1.0.15

# Small amount of customisation required, mainly to do our own quote style.
# these are the the other options available to the parser:

# newline (default: '<br />')
# What to replace newlines with.
# normalize_newlines (default: True)
# Whether to convert CR and CRLF to LF before replacements.
# install_defaults (default: True)
# Whether to install the default tag formatters. If False, you will need to specify add tag formatters yourself.
# escape_html (default: True)
# Whether to escape special HTML characters (<, >, &, ”, and ‘). Replacements are specified as tuples in Parser.REPLACE_ESCAPE.
# replace_links (default: True)
# Whether to automatically create HTML links for URLs in the source text.
# replace_cosmetic (default: True)
# Whether to perform cosmetic replacements for —, –, ..., (c), (reg), and (tm). Replacements are specified as tuples in Parser.REPLACE_COSMETIC.
# tag_opener (default: '[')
# The opening tag character(s).
# tag_closer (default: ']')
# The closing tag character(s).
# linker (default: None (use the built-in link replacement))
# A function that takes a regular expression match object (and optionally the Parser context) and returns an HTML replacement string.
# linker_takes_context (default: False)
# Whether the linker function accepts a second context parameter. If True, the linker function will be passed the context sent to Parser.format.
# drop_unrecognized (default: False)
# Whether to drop unrecognized (but valid) tags. The default is to leave the tags, unformatted, in the output.

import bbcode

parser = bbcode.Parser(replace_links=False) # oembed (micawber) handles link replacements

# custom quote formatter, display username
def render_quote(tag_name, value, options, parent, context):
	author = u''
	# [quote=Somebody]
	if 'quote' in options:
		author = options['quote']
	extra = '<span class="quote-author">%s wrote:</span>' % author if author else ''
	return '<div class="quote-msg">%s %s</div>' % (extra, value)

# Now register our new quote tag, telling it to strip off whitespace, and the newline after the [/quote].
parser.add_formatter('quote', render_quote, strip=True, swallow_trailing_newline=True)
# Add an image formatter
def render_image(tag_name, value, options, parent, context):
	""" Render an image tag. Do a quick check on extension
	to see if it's an image type. """
	import urlparse, os
	src = ''
	if 'img'in options:
		# in case someone does img=http...
		src = options['img']
	else:
		src = value
	path = urlparse.urlparse(src).path
	ext = os.path.splitext(path)[1]
	if ext.lower() in ['.jpeg', '.gif', '.png', '.jpg']:
		return '<img src="%s">' % (value,)
	else:
		return ''
	
parser.add_formatter('img', render_image, strip=True, swallow_trailing_newline=True)
fukparser = parser