# Excellent who's online code from Eric Florenzano
# https://gist.github.com/268379
# Altered to store the usernames in the cache as well.

from django.core.cache import cache
from django.conf import settings

from django.contrib.auth.models import User

ONLINE_THRESHOLD = getattr(settings, 'ONLINE_THRESHOLD', 60 * 15)
ONLINE_MAX = getattr(settings, 'ONLINE_MAX', 50)


def get_online_now(self):
    return User.objects.filter(id__in=self.online_now_ids or [])


class OnlineNowMiddleware(object):
    """
    Maintains a list of users who have interacted with the website recently.
    Their user IDs are available as ``online_now_ids`` on the request object,
    and their corresponding users are available (lazily) as the
    ``online_now`` property on the request object.
    A third property on the request contains a dict of user ids and usernames
    so we can easily create a link to their profile without generating 
    separate db call.
    """

    def process_request(self, request):
        # First get the index
        uids = cache.get('online-now', [])
   
        # Perform the multiget on the individual online uid keys
        online_keys = ['online-%s' % (u,) for u in uids]
        fresh = cache.get_many(online_keys)
        online_now_ids = [int(k.replace('online-', '')) for k in fresh.keys()]
        online_now_users = dict([(int(k.replace('online-', '')), fresh[k]) for k in fresh.keys()])

        # If the user is authenticated, add their id to the list
        if request.user.is_authenticated():
            uid = request.user.id
            # If their uid is already in the list, we want to bump it
            # to the top, so we remove the earlier entry.
            if uid in online_now_ids:
                online_now_ids.remove(uid)
            online_now_ids.append(uid)
            online_now_users[uid] = request.user.username
            if len(online_now_ids) > ONLINE_MAX:
                del online_now_ids[0]

        # Attach our modifications to the request object
        request.__class__.online_now_ids = online_now_ids
        request.__class__.online_now_users = online_now_users
        request.__class__.online_now = property(get_online_now)
        
        # Set the new cache
        if request.user.is_authenticated():
            cache.set('online-%s' % (request.user.pk,), request.user.username,
                 ONLINE_THRESHOLD)
        cache.set('online-now', online_now_ids, ONLINE_THRESHOLD)
