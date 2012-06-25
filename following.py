#!/usr/bin/env python

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import oauth2 as oauth

CONSUMER_KEY = ''
CONSUMER_SECRET = ''

OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''

def main():

    consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    token = oauth.Token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    client = oauth.Client(consumer, token)

    response, content = client.request("http://api.tumblr.com/v2/user/following", method="POST")

    print(response)
    print(content)

if __name__ == "__main__":
    main()

