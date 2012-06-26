#!/usr/bin/env python

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import ConfigParser
import argparse

import simplejson as json
import httplib

import os

from random import choice

from tumblr import Tumblr

def parseArgs():
    parser = argparse.ArgumentParser(description='Retrieve Photo Posts')
    parser.add_argument('config', help='The config file')
    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args.config)

    return config

def parseBlogPhotos(posts):
    output = []
    for post in posts:
        url    = post['post_url']
        date   = post['date']
        photos = post['photos']
        for photo in photos:
            url = photo['original_size']['url']
            name, ext = os.path.splitext(url)

            if ext == '.jpg' or ext == '.jpeg':
                data = {}
                data['url']   = url
                data['date']  = date
                output.append(data)

    return output


# Go through parsing the response for each blog
def getFollowerPhotos(followers, tumblr):

    finalData = []

    for blog in followers:

        blogurl = blog['url']
        # Cut off leading 'http://'
        info = tumblr.getPosts(blogurl[7:], 'photo')

        if info['meta']['status'] != 200:
            print('could not get posts for %s' % blogurl)
        else:
            response = info['response']
            blogName = response['blog']['title']
            photos = parseBlogPhotos(response['posts'])
            if photos:
                blogData ={}
                blogData['name']   = blogName
                blogData['url']    = blogurl
                blogData['photos'] = photos
                finalData.append(blogData)

    return finalData

def getPhoto(data):
    blog = choice(data)
    image = choice(blog['photos'])
    data = {}
    data['name']  = blog['name']
    data['url']   = blog['url']
    data['image'] = image['url']
    data['date']  = image['date']
    return data

def main():

    config = parseArgs()
    consumerKey    = config.get('consumer', 'key')
    consumerSecret = config.get('consumer', 'secret')
    oauthToken     = config.get('oauth', 'key')
    oauthSecret    = config.get('oauth', 'secret')

    tumblr = Tumblr(consumerKey, consumerSecret, oauthToken, oauthSecret)
    tumblr.authenticate()

    data = tumblr.getFollowing()

    followers = data['blogs']

    allData =  getFollowerPhotos(followers, tumblr)

    print(getPhoto(allData))


if __name__ == '__main__':
    main()

