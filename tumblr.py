
import oauth2 as oauth
import simplejson as json

class Tumblr(object):

    def __init__(self, consumerKey, consumerSecret, oauthKey, oauthSecret):
        self.cKey    = consumerKey
        self.cSecret = consumerSecret

        self.oKey    = oauthKey
        self.oSecret = oauthSecret

        self.baseUrl = 'api.tumblr.com/v2/'

    def authenticate(self):
        self.consumer = oauth.Consumer(self.cKey, self.cSecret)
        self.token = oauth.Token(self.oKey, self.oSecret)
        self.client = oauth.Client(self.consumer, self.token)

    def getFollowing(self):
        url = 'http://%suser/following' % self.baseUrl
        response, content = self.client.request(url, method='POST')
        return json.loads(content)['response']



