import requests
import logging

#SFS_API_URL = 'http://www.wunonb.dev/api?'
SFS_API_URL = 'http://www.stopforumspam.com/api?'

logger = logging.getLogger('fukapp.registration')

def check_sfs(ip, email):
  """ Check IP, email & username at StopForumSpam
  Returns JSON in the format:  
  {"success":1,"email":{"lastseen":"2012-09-13 14:14:32","frequency":969,
  "appears":1,"confidence":99.85},"ip":{"frequency":0,"appears":0}}
  We let requests lib handle the exceptions and simply log
  an error if we don't have a valid JSON response, but let the 
  registration go ahead anyway so as not to piss off valid punters.
  """

  data ={'ip': ip, 'email':email, 'f': 'json'}
  try:
    r = requests.get(SFS_API_URL, params=data)
  except requests.ConnectionError:
    logger.warning("Connection error, could not validate email.")
    return True
  try:
    j = r.json()
  except ValueError:
    logger.warning("No valid response from SFS server")
    return True
  mail = j.get("email")
  if mail and mail["appears"]:
    return False
  return True


