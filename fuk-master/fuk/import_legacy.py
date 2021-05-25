import os
import argparse
from django.conf import settings
import datetime

from django.contrib.auth.models import User, Group
from django.db import connection


category_map = {
  '35': '1',
  '34': '2',
  '41': '3',
  '59': '5',
  '65': '6',
  '38': '7',
  '53': '8',
  '60': '9',
  '55': '2', # putting competitions into general discussion, better check with Brad!
}

tables=['node', 'node_comment_statistics', 'node_revisions', 'term_node', 'users', 'comments',  'profile_values', 'flatforum', 'users_roles', 'privatemsg', 'privatemsg_archive', 'url_alias']




dbs = getattr(settings, 'DATABASES')

db_name = dbs['default']['NAME']
db_user = dbs['default']['USER']
db_pass = dbs['default']['PASSWORD']

def load_db_tables():
  """ Get the current drupal database tables from backup and load in to live site.
  
  Careful with this, each call to Popen opens a new process, and these can take a while
  to complete. Might be better to do one at a time and poll for return code?

  """
  import subprocess

  
  os.chdir(path_to_data)
  for t in tables:
    if os.path.exists(t+'.sql.bz2'):
      if subprocess.call(['bunzip2', t+'.sql.bz2']) !=0:
        print "Error unzipping %s" % t
    if os.path.exists(t+'.sql'):
      print "Loading %s" % t
      call='mysql -u %s --password=%s %s < %s' % (db_user, db_pass, db_name, t+'.sql') 
      if subprocess.check_call(call, shell=True) != 0:
        print "Error loading %s" % t
      
    

  
def load_users():
  """Load the user table, truncating any usernames that are longer than 30 characters. (there aren't many of them), and excluding user 1"""
  cursor = connection.cursor()
  # get rid of some shit 
  # long usernames are a problem. I think we need to delete the long ones and hope that they haven't posted. This will need checking before final upload.
  # cursor.execute("DELETE FROM users WHERE name LIKE 'buy %'")doesn't like % string in query
  cursor.execute("DELETE FROM auth_user WHERE id != 1")
  cursor.execute("DELETE FROM `users` WHERE LENGTH(name) > 30")
  cursor.execute("INSERT INTO auth_user(id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) SELECT uid, SUBSTRING(name, 1, 30), '', '', mail, pass, 0, 1, 0, FROM_UNIXTIME(login), FROM_UNIXTIME(created) FROM users WHERE access !=0 AND uid != 1")
  cursor.close()


def load_topics():
  print "Loading topics"
  # deal with the ones with duplicate terms entries
  cursor = connection.cursor()
  # remove foreign key constraint, or we'll get an error on truncate
  cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
  cursor.execute("TRUNCATE TABLE snapboard_thread")
  cursor.execute("DELETE FROM term_node WHERE nid=52811 AND tid=35;")  
  cursor.execute("DELETE FROM term_node WHERE nid=53347 AND tid=34;")
  cursor.execute("DELETE FROM term_node WHERE nid=63624 AND tid=34;")
  cursor.execute("INSERT INTO snapboard_thread(id, user_id, name, slug, category_id, private, closed, sticky, created, updated, last_poster_id, post_count, show_og, popular) SELECT DISTINCT n.nid, n.uid, n.title, '', t.tid, 0, 0, 0, FROM_UNIXTIME(n.created), FROM_UNIXTIME(ncs.last_comment_timestamp), ncs.last_comment_uid, ncs.comment_count+1, 0, 0 FROM node n LEFT JOIN node_comment_statistics ncs ON ncs.nid = n.nid LEFT JOIN term_node t ON t.nid = n.nid WHERE n.type = 'forum' AND n.status = 1 AND ncs.last_comment_timestamp > 0 AND ncs.last_comment_uid IS NOT NULL AND t.tid IS NOT NULL")
  # transaction.commit_unless_managed()
  # remap category ids
  ks=category_map.keys()
  for k in ks:
    cursor.execute("UPDATE snapboard_thread SET category_id = %s WHERE category_id = %s", [category_map[k], k])
  # update url path /slugs
  cursor.execute('CREATE TABLE `url_map` (`nid` INT(11) NOT NULL, `path` VARCHAR(128) NOT NULL) ENGINE = MyISAM;') 
  cursor.execute('INSERT INTO url_map(nid, path) SELECT SUBSTRING(src, 6), SUBSTRING(dst, 9) FROM url_alias WHERE src NOT LIKE "%%/feed" AND src NOT LIKE "forum/%%" AND dst LIKE "threads/%%"')
  cursor.execute("UPDATE snapboard_thread st, url_map um SET st.slug=um.path WHERE st.id=um.nid AND um.path REGEXP '^[a-z0-9A-Z_\-]+$'")
  cursor.execute('DROP TABLE url_map')
  cursor.close()
  
def rewrite_slugs():
  from snapboard.models import Thread
  from snapboard.utils import SlugifyUniquely
  print "Rewriting slugs"
  cursor = connection.cursor()
  noslugs = Thread.objects.all().filter(slug='')
  for thread in noslugs:
    # todo this does not avoid duplicate threads - check!
    thread.slug=SlugifyUniquely(thread.name, Thread)
    thread.save()
  # a few junky ones might be left, delete them
  cursor.execute("DELETE FROM `snapboard_thread` WHERE slug=''")
  cursor.close()
  
  
  
def load_posts():
  """ Load all the old posts. You really don't want to do this too often, so try and limit to posts that have been updated since the last run."""
  cursor = connection.cursor()
  print "Loading posts"
  # load all the first posts
  cursor.execute("TRUNCATE TABLE snapboard_post")
  cursor.execute("INSERT INTO snapboard_post(`user_id`, `thread_id`, `text`, `status`, `date`, `edited`, `ip`) SELECT n.uid, n.nid, v.body, 'a', FROM_UNIXTIME(n.created), FROM_UNIXTIME(n.created), '0.0.0.0' FROM node n LEFT JOIN node_revisions v ON n.vid = v.vid WHERE n.type= 'forum' AND n.status = 1 ORDER BY n.created ASC")
  cursor.execute("INSERT INTO snapboard_post(`user_id`, `thread_id`, `text`, `status`, `date`, `edited`, `ip`) SELECT c.uid, c.nid, c.comment, 'a', FROM_UNIXTIME(c.timestamp), FROM_UNIXTIME(c.timestamp), c.hostname FROM comments c LEFT JOIN node n ON c.nid=n.nid WHERE n.type='forum' ORDER BY c.cid ASC")
  cursor.close()
  
def load_profiles():
  print "Loading profiles"
  cursor = connection.cursor()
  cursor.execute("TRUNCATE fprofiles_userprofile")
  # deal with weird excessive post counts.
  cursor.execute("UPDATE flatforum SET posts = 100 WHERE posts > 100000")
  # create profile records for all users
  sql = "INSERT INTO fprofiles_userprofile(`user_id`, `location`, `website`, `twitter`, `postnotify`, `messagenotify`, `postcount`,  `moderated_posts`) SELECT id, '', '', '', 'd', 'd', '0', '0' FROM auth_user"
  cursor.execute(sql)
  # now, update with full profile data, in separate queries due to the way profiles organised in old db
  cursor.execute("UPDATE fprofiles_userprofile fp, users u SET fp.lastactive = FROM_UNIXTIME(u.access) WHERE fp.user_id = u.uid")
  cursor.execute("UPDATE fprofiles_userprofile fp, flatforum f SET fp.postcount=f.posts WHERE fp.user_id=f.uid")
  cursor.execute("UPDATE fprofiles_userprofile fp, profile_values pv SET fp.location=SUBSTRING(pv.value, 1, 64) WHERE pv.fid=1 AND pv.uid=fp.user_id")
  cursor.execute("UPDATE fprofiles_userprofile fp, profile_values pv SET fp.website=SUBSTRING(pv.value, 1, 64) WHERE pv.fid=5 AND pv.uid=fp.user_id")
  cursor.execute("UPDATE fprofiles_userprofile SET moderated_posts = postcount WHERE postcount <= 9")
  cursor.execute("UPDATE fprofiles_userprofile SET moderated_posts = 10 WHERE postcount > 9")
  cursor.close()  
  
def load_avatars():
  """Find the user's old avatar and add it to their account
  Use the AVLOCATION environment variable which is actually
  a root path to the existing site install (the rest of the path
    is stored in the db entry)

  Note that saving an image to the avatars dir requires webserver perms.
  """
  import os
  from fprofiles.models import Avatar
  from django.contrib.auth.models import User
  from django.core.files import File
  cursor = connection.cursor()
  cursor.execute("TRUNCATE fprofiles_avatar")
  sql = "SELECT uid, picture FROM users WHERE picture != ''"
  cursor.execute(sql)
  avs = cursor.fetchall()
  for uid, pic in avs:
    u = User.objects.get(id=uid)
    av = os.path.join(av_location, pic)
    if os.path.exists(av):
      fh = File(open(av))
      try:
        avatar = u.useravatar
        print "User %d already has an avatar" % uid
        return
      except Avatar.DoesNotExist:
        avatar = Avatar(user=u)
        avatar.avatar.save(os.path.basename(av), fh)
  cursor.close()
      
    

# load the pm table and create umessages from each one!

def load_pms():
  """Load all the pms"""
  cursor = connection.cursor()
  cursor.execute('TRUNCATE umessages_message')
  cursor.execute('TRUNCATE umessages_messagerecipient')
  # get all the messages
  # Have had to replace the original queries that did this with more rigorous ones
  # due to foreign key constraint errors when using InnoDB tables.
  # The first one checks that the sender exists in the user table:
  sql = "INSERT INTO umessages_message (id, body, sender_id, sent_at) (SELECT p.id, p.message, p.author, FROM_UNIXTIME(p.timestamp) FROM privatemsg p LEFT JOIN auth_user ON p.author = auth_user.id WHERE auth_user.id IS NOT NULL)"
  cursor.execute(sql)
  # The second checks that the recipient exists in the user table, and that
  # the message exists in the message table.
  sql2 = "INSERT INTO umessages_messagerecipient (user_id, message_id, read_at) (SELECT p.recipient, p.id, FROM_UNIXTIME(p.timestamp) FROM privatemsg p LEFT JOIN umessages_message ON p.id = umessages_message.id LEFT JOIN auth_user ON p.recipient = auth_user.id WHERE umessages_message.id IS NOT NULL AND auth_user.id IS NOT NULL)"
  cursor.execute(sql2)
  cursor.close()
  
  
def contact_updater_2():
  """ Go down through the message table creating contact objects for latest message. 
  Check for highest existing message id, so that we can update."""
  
  cursor = connection.cursor()
  cursor.execute("SELECT MAX(latest_message_id) FROM umessages_messagecontact")
  x = cursor.fetchone()
  maxid = x[0] or 0
  if maxid > 0:
    from userena.contrib.umessages.models import Message
    # we are in update mode, use native umessages methods.
    # Get the new messages in ascending order and update the contacts
    msgs = Message.objects.filter(pk__gt=maxid).order_by('id')
    for m in msgs:
      m.update_contacts(m.recipients.all())
  else: 
    n = cursor.execute("SELECT m.sender_id, r.user_id, m.id FROM umessages_message m, umessages_messagerecipient r WHERE m.id = r.message_id ORDER BY m.id DESC")
    # n=cursor.execute("SELECT author, recipient, id FROM privatemsg WHERE id > %d ORDER BY id DESC" % (maxid,))
    r = cursor.fetchall()
    # create an array to keep track contacts we have processed
    pairs = set()
    ct = 0
    cursor.execute("SET autocommit=0")
    cursor.execute("SET unique_checks=0")
    cursor.execute("SET foreign_key_checks=0")
    for m in r:
      ct += 1
      if ct % 1000 == 0:
        cursor.execute("COMMIT")
        print "%d of %d" % (ct, n)
      contact1 = (m[0], m[1])
      if contact1 in pairs:
        # check for one of the contact pairs. As we add both, we only need
        # to check for one.
        continue
      else:
        contact2 = (m[1], m[0])
        sql = "INSERT INTO umessages_messagecontact (from_user_id, to_user_id, latest_message_id) VALUES (%d, %d, %d)" % m
        cursor.execute(sql)
        pairs.add(contact1)
        pairs.add(contact2)
  # # tidy up database, removed deleted users.
  # cursor.execute("DELETE f FROM auth_user AS u RIGHT OUTER JOIN umessages_messagecontact AS f ON u.id = f.from_user_id WHERE u.username IS NULL")
  # cursor.execute("DELETE f FROM auth_user AS u RIGHT OUTER JOIN umessages_messagecontact AS f ON u.id = f.to_user_id WHERE u.username IS NULL")
  cursor.execute("COMMIT")
  cursor.execute("SET autocommit=1")
  cursor.execute("SET unique_checks=1")
  cursor.execute("SET foreign_key_checks=1")
  cursor.close()


  
def do_role_update(sql, group):
  cursor = connection.cursor()
  cursor.execute(sql)
  bs = cursor.fetchall()
  for b in bs:
    try:
      u = User.objects.get(id=b[0])
      u.groups.add(group)
    except User.DoesNotExist: # we may have scrubbed the user in the import
      pass
  cursor.close()


def update_roles():
  """ Copy role (gj, mod) info over """
  j = connection.cursor()
  j.execute('TRUNCATE auth_user_groups')
  gj = Group.objects.get(name="Goldens")
  basics = Group.objects.get(name="Basics")
  mods = Group.objects.get(name="Mods")
  
  basicsql = "SELECT user_id FROM fprofiles_userprofile WHERE moderated_posts > 0"
  gjsql = "SELECT uid FROM users_roles WHERE rid = 3"
  modsql = "SELECT uid FROM users_roles WHERE rid = 4"

  do_role_update(basicsql, basics)
  do_role_update(gjsql, gj)
  do_role_update(modsql, mods)
  # make brad a superuser
  brad = User.objects.get(pk=5)
  brad.is_staff=True
  brad.is_superuser=True
  brad.save()
  j.close()

def main():
  start=datetime.datetime.now()
  print "Loading original data"
  load_db_tables()
  print "Loading users"
  load_users()
  load_topics()
  print "Loading posts"
  load_posts()
  rewrite_slugs()
  # fix_youtube()
  print "Loading profiles"
  load_profiles()
  print "Updating roles"
  update_roles()
  print "Loading avatars"
  load_avatars()
  print "Loading PMs"
  load_pms()
  contact_updater_2()
  elapsed = datetime.datetime.now() - start
  print "Script took %d minutes to execute" % (elapsed.seconds/60,)

  
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Import legacy fuk data to nufuk.')
  
  parser.add_argument('-a', '--avpath', type=str, required=True)
  parser.add_argument('-d', '--dbpath', type=str, required=True)
  args = parser.parse_args()
  path_to_data = args.dbpath
  av_location = args.avpath
  main()
"""
-- create a temp table for the url aliases

CREATE TABLE IF NOT EXISTS `url_map` (`nid` INT(11) NOT NULL, `path` VARCHAR(64) NOT NULL) ENGINE = MyISAM;

INSERT INTO url_map(nid, path) SELECT SUBSTRING(src, 6), SUBSTRING(dst, 9) FROM url_alias WHERE src NOT LIKE "%/feed" AND dst LIKE "threads/%"

-- this leaves us with a lot of characters that won't work in the django slug system, so lets find out which ones they are 

SELECT * FROM url_map WHERE path NOT REGEXP '^[a-z0-9A-Z_\-]+$' 
-- about 1000 urls that need sorting. A plan? 

-- Databsase query to load up old users.
-- Be aware that users with no login entry in their drupal row will end up with 1970-01-01 in django. Might need to filter this.


INSERT INTO auth_user(id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) SELECT uid, name, '', '', mail, CONCAT('md5$$', pass), 0, 1, 0, FROM_UNIXTIME(login), FROM_UNIXTIME(created) FROM users WHERE access !=0

-- Deal with the posts. We need to 
-- Create categories that match the old ones. 
-- Create topics using old nids, so we can map if need be. Topics (nodes), should join on node_comment_statistics and taxonomy to get at the category.
--  dupe node 52811, 53347, 63624
DELETE FROM term_node WHERE nid=52811 AND tid=35;
DELETE FROM term_node WHERE nid=53347 AND tid=34;
DELETE FROM term_node WHERE nid=63624 AND tid=34;

INSERT INTO snapboard_thread(id, user_id, name, slug, category_id, private, closed, sticky, created, updated, last_poster_id, post_count) SELECT DISTINCT n.nid, n.uid, n.title, '', t.tid, 0, 0, 0, FROM_UNIXTIME(n.created), FROM_UNIXTIME(ncs.last_comment_timestamp), ncs.last_comment_uid, ncs.comment_count FROM node n LEFT JOIN node_comment_statistics ncs ON ncs.nid = n.nid LEFT JOIN term_node t ON t.nid = n.nid WHERE n.type = 'forum' AND n.status = 1

User roles

1 anonymous user
2 authenticated user
3 fuk elite
4 moderator
5 admin
6 editor
7 advertiser
8 BANner


Tables required from live DB:

node
node_comment_statistics
node_revisions
term_node
users
comments
profile_values
flatforum
"""
