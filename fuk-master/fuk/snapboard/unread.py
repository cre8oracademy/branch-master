from snapboard.models import Thread, Post, Read

# Unreads code borrowed from pyBB.

def cache_unreads(qs, user):
    if not len(qs) or not user.is_authenticated():
        return qs
    if isinstance(qs[0], Thread):
        reads = Read.objects.filter(thread__pk__in=set(x.id for x in qs),
            user=user).select_related()
        read_map = dict((x.thread.id, x) for x in reads)

        for thread in qs:
            thread._read = read_map.get(thread.id, None)
        return qs
    elif isinstance(qs[0], Post):
        ids = set(x.thread.id for x in qs)
        reads = Read.objects.filter(thread__pk__in=ids, user=user).select_related()
        read_map = dict((x.thread.id, x) for x in reads)

        for post in qs:
            post.thread._read = read_map.get(post.thread.id, None)
        return qs
    else:
        raise Exception('cache_unreads could process only Post or Thread querysets')
