#!/usr/bin/env python

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import oauth2 as oauth
import simplejson as json
import httplib

CONSUMER_KEY = ''
CONSUMER_SECRET = ''

OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''

def main():

    consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    token = oauth.Token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    client = oauth.Client(consumer, token)

    response, content = client.request("http://api.tumblr.com/v2/user/following", method="POST")

    con = httplib.HTTPConnection("api.tumblr.com")
    data = json.loads(content)
    for blog in data["response"]["blogs"]:
        blogurl = blog["url"][7:]
        req_url = "/v2/blog/" + blogurl + "/posts/photo"
        query = req_url + "?api_key=" + CONSUMER_KEY
        con.request("GET", query)
        r1 = con.getresponse()

        print r1.read()

if __name__ == "__main__":
    main()

