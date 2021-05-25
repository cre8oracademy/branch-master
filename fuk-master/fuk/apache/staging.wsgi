import os
import sys
import site


vepath='/home/fuk/staging/fuk-env/lib/python2.6/site-packages'
prev_sys_path = list(sys.path)

# add the site-packages of our virtualenv as a site dir
site.addsitedir(vepath)

# add the app's directory to the PYTHONPATH
sys.path.append('/home/fuk/staging/')
sys.path.append('/home/fuk/staging/fuk/')

# reorder sys.path so new directories from the addsitedir show up first
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

# import from down here to pull in possible virtualenv django install
from django.core.handlers.wsgi import WSGIHandler
os.environ['DJANGO_SETTINGS_MODULE'] = 'fuk.settings'
application = WSGIHandler()

