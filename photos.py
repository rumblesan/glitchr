#!/usr/bin/env python

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import ConfigParser
import argparse

import oauth2 as oauth
import simplejson as json
import httplib

CONSUMER_KEY = ''
CONSUMER_SECRET = ''

OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''


def parseArgs():
    parser = argparse.ArgumentParser(description='Retrieve Photo Posts')
    parser.add_argument('config', help='The config file', required=True)
    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args.config)

    return config

def main():

    config = parseArgs()

    consumer_key    = config.get('consumer', 'key')
    consumer_secret = config.get('consumer', 'secret')

    oauth_token     = config.get('oauth', 'key')
    oauth_secret    = config.get('oauth', 'secret')

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    token = oauth.Token(oauth_token, oauth_secret)
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

