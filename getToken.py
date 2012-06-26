#!/usr/bin/env python

# Basic script used to get OAUTH Tokens from tumblr

import ConfigParser
import argparse

import oauth2 as oauth
import urlparse

CONSUMER_KEY = ''
CONSUMER_SECRET = ''


def parseArgs():
    parser = argparse.ArgumentParser(description='Retrieve Photo Posts')
    parser.add_argument('config', help='The config file', required=True)
    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args.config)

    return config

def main():
    REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
    AUTHORIZATION_URL = 'http://www.tumblr.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'

    config = parseArgs()
    consumer_key    = config.get('consumer', 'key')
    consumer_secret = config.get('consumer', 'secret')

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    resp, content = client.request(REQUEST_TOKEN_URL, "GET")
    request_token = dict(urlparse.parse_qsl(content))

    print "Go to the following link in your browser:"
    print "%s?oauth_token=%s" % (AUTHORIZATION_URL, request_token['oauth_token'])
    print 

    accepted = 'n'
    while accepted.lower() == 'n':
        accepted = raw_input('Have you authorized me? (y/n) ')
    oauth_verifier = raw_input('What is the PIN? ')

    token = oauth.Token(request_token['oauth_token'],
        request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(ACCESS_TOKEN_URL, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    print access_token
    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print
    print "You may now access protected resources using the access tokens above." 
    print

if __name__ == "__main__":
    main()

