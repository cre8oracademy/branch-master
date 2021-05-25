##Fleshing out a strategy

Key pain points on the raw system are that there are way too many repeated requests for things like user info (although this sort of stuff is very quick to get from the query cache) and long slow queries for threads.

Threads get hit a couple of times, firstly to count and determine the pagination, second to get the actual posts. If the post count was stored on the thread itself, that would speed the first count dramatically, but it would mean keeping that value up-to-date. There are already issues with post counts being out of sync that seem to be duplicating the current problems with threads displaying the last-but-one page.

[2012-11-08 5:13:46] We now store the post count separately so, that speeds up lots of renders which need to know how many pages there, and pagination.

###The per-view cache

Caching an individual page of a view would give a great boost on regularly accessed pages. Django's built in view cache stores the entire page (I think!), rather than just the bits in the view code, so this cannot be done with the out-of-the-box method. Caching with more granularity should be possible, but invalidation is tricky.

(just thought of a way of doing this though - if you create a cache prefix that uses something on the thread that will change, eg the number of posts, you could allow the old ones to expire without explicity invalidating them).

###Active threads caching

The active threads on the sidebar uses a fairly complex bit of caching code, to account for the fact that different users will have permissions for different threads. When a thread is updated, it adds itself to a list in the cache of recently updated threads (update_active_threads method in models.py). The template tag looks for these values and builds the appropriate list for the user, but this is going to be very slow to update after a cache empty/server restart or whatever. A utility function that works through the most recent threads would be a good idea here, as the block is called so often. 

For anonymous users, it will just load the whole cached page, so not an issue.
