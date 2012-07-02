#!/usr/bin/env python

# Basic script used to get OAUTH Tokens from tumblr

from sys import argv
from tumblpy import Tumblpy
from ConfigParser import SafeConfigParser

def main():
    configFile = argv[1]

    config = SafeConfigParser()
    config.read(configFile)

    consumer_key    = config.get('consumer', 'key')
    consumer_secret = config.get('consumer', 'secret')

    tumblr = Tumblpy(consumer_key, consumer_secret)
    auth_props = tumblr.get_authentication_tokens()

    print("Go to the following link in your browser:")
    print(auth_props['auth_url'])
    print('')

    oauth_verifier = 'n'
    while oauth_verifier.lower() == 'n':
        oauth_verifier = raw_input('What is the PIN?:  ')

    tumblr = Tumblpy(consumer_key,
                     consumer_secret,
                     auth_props['oauth_token'],
                     auth_props['oauth_token_secret'])

    authorized_tokens = tumblr.get_access_token(oauth_verifier)

    config.set('oauth', 'key', authorized_tokens['oauth_token'])
    config.set('oauth', 'secret', authorized_tokens['oauth_token_secret'])
    
    print('Saving keys to config file %s' % configFile)

    with open(configFile, 'w') as fp:
        config.write(fp)

if __name__ == "__main__":
    main()

