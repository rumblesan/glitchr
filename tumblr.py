
import oauth2 as oauth
import simplejson as json
import urllib2
import urllib

class Tumblr(object):

    def __init__(self, consumerKey, consumerSecret, oauthKey, oauthSecret):
        self.cKey    = consumerKey
        self.cSecret = consumerSecret

        self.oKey    = oauthKey
        self.oSecret = oauthSecret

        self.baseUrl = 'http://api.tumblr.com/v2'

    def authenticate(self):
        self.consumer = oauth.Consumer(self.cKey, self.cSecret)
        self.token = oauth.Token(self.oKey, self.oSecret)
        self.client = oauth.Client(self.consumer, self.token)

    def getFollowing(self):
        url = '%s/user/following' % self.baseUrl
        response, content = self.client.request(url, method='POST')
        return json.loads(content)['response']

    def getPosts(self, blogName, postType=None):

        url = '%s/blog/%s/posts' % (self.baseUrl, blogName)
        if postType:
            url += '/%s' % postType

        params = {}
        params['api_key'] = self.cKey
        url += '?%s' % urllib.urlencode(params)

        req = urllib2.Request(url=url)
        f = urllib2.urlopen(req)
        data = f.read()
        return json.loads(data)


