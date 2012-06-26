
import urllib2

class TumblrPhoto(object):

    def __init__(self, url):
        self.url = url

    def retrieve(self):
        req = urllib2.Request(url=self.url)
        f = urllib2.urlopen(req)
        self.data = f.read()

    def save(self, fileName):
        of = open(fileName, 'wb')
        of.write(self.data)
        of.close()

