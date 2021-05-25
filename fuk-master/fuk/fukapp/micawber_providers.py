from django.core.cache import cache
from micawber.providers import Provider, ProviderRegistry

EMBEDLY_KEY = '26ee36b806f411e1936a4040d3dc5c07'



class ImageProvider(Provider):
    """
    Simple little hack to render any image URL as an <img> tag, use with care

    Usage:

    pr = micawber.bootstrap_basic()
    pr.register(ImageProvider.regex, ImageProvider(''))
    """
    regex = 'http://.+?\.(jpg|gif|png)'

    def request(self, url, **params):
        return {
            'url': url,
            'type': 'photo',
            'title': '',
        }



def oembed_providers():
    """ Register oembed providers.
    The list below is taken from Micawbers bootstrap_basic function, with various irrelevant
    and error-prone providers removed. It should be maintained fairly regularly, as new
    stuff shows up on the Micawber list often.
    """
    pr = ProviderRegistry(cache)
    # Providers that are not included in micawber's bootstrap_basic
    pr.register(ImageProvider.regex, ImageProvider(''))
    pr.register("http://open.spotify.com/*", Provider('http://api.embed.ly/1/oembed', key=EMBEDLY_KEY))

    # micawber bootstrap basic providers
    pr.register('http://blip.tv/\S+', Provider('http://blip.tv/oembed'))
    
    # c
    pr.register('http://chirb.it/\S+', Provider('http://chirb.it/oembed.json'))
    
    # d
    
    # f
    pr.register('http://\S*?flickr.com/\S+', Provider('http://www.flickr.com/services/oembed/'))
    pr.register('http://flic\.kr/\S*', Provider('http://www.flickr.com/services/oembed/'))
    pr.register('https?://(www\.)?funnyordie\.com/videos/\S+', Provider('http://www.funnyordie.com/oembed'))
    
    # g
    
    # h
    pr.register('http://www.hulu.com/watch/\S+', Provider('http://www.hulu.com/api/oembed.json'))
    
    # i
    pr.register('http://\S*imgur\.com/\S+', Provider('http://api.imgur.com/oembed')),
    pr.register('http://instagr(\.am|am\.com)/p/\S+', Provider('http://api.instagram.com/oembed'))
    
    # j
    
    # m
    pr.register('http://www.mobypicture.com/user/\S*?/view/\S*', Provider('http://api.mobypicture.com/oEmbed'))
    pr.register('http://moby.to/\S*', Provider('http://api.mobypicture.com/oEmbed'))
    
    # p
    pr.register('http://i\S*.photobucket.com/albums/\S+', Provider('http://photobucket.com/oembed'))
    pr.register('http://gi\S*.photobucket.com/groups/\S+', Provider('http://photobucket.com/oembed'))
    pr.register('http://www.polleverywhere.com/(polls|multiple_choice_polls|free_text_polls)/\S+', Provider('http://www.polleverywhere.com/services/oembed/'))
    pr.register('https?://(.+\.)?polldaddy\.com/\S*', Provider('http://polldaddy.com/oembed/'))
    
    # q
    pr.register('http://qik.com/video/\S+', Provider('http://qik.com/api/oembed.json'))
    
    # r
    pr.register('http://\S*.revision3.com/\S+', Provider('http://revision3.com/api/oembed/'))
    
    # s
    pr.register('http://www.slideshare.net/[^\/]+/\S+', Provider('http://www.slideshare.net/api/oembed/2'))
    pr.register('http://slidesha\.re/\S*', Provider('http://www.slideshare.net/api/oembed/2'))
    pr.register('http://\S*.smugmug.com/\S*', Provider('http://api.smugmug.com/services/oembed/'))
    pr.register('https://\S*?soundcloud.com/\S+', Provider('http://soundcloud.com/oembed'))
    pr.register('https?://speakerdeck\.com/\S*', Provider('https://speakerdeck.com/oembed.json')),
    pr.register('https?://(www\.)?scribd\.com/\S*', Provider('http://www.scribd.com/services/oembed'))
    
    # t
    pr.register('https?://(www\.)?twitter.com/\S+/status(es)?/\S+', Provider('https://api.twitter.com/1/statuses/oembed.json'))
    
    # v
    pr.register('http://\S*.viddler.com/\S*', Provider('http://lab.viddler.com/services/oembed/'))
    pr.register('http://vimeo.com/\S+', Provider('http://vimeo.com/api/oembed.json', maxwidth="576"))
    # vimeo needs a maxwidth, or it returns huge vids
    pr.register('https://vimeo.com/\S+', Provider('https://vimeo.com/api/oembed.json', maxwidth="576"))
    
    # y
    pr.register('http://(\S*.)?youtu(\.be/|be\.com/watch)\S+', Provider('http://www.youtube.com/oembed'))
    pr.register('https://(\S*.)?youtu(\.be/|be\.com/watch)\S+', Provider('http://www.youtube.com/oembed?scheme=https&'))
    pr.register('http://(\S*\.)?yfrog\.com/\S*', Provider('http://www.yfrog.com/api/oembed'))
    
    # w
    pr.register('http://\S+.wordpress.com/\S+', Provider('http://public-api.wordpress.com/oembed/'))
    pr.register('https?://wordpress.tv/\S+', Provider('http://wordpress.tv/oembed/'))
    
    return pr
    
