#!/usr/bin/env python

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import ConfigParser
import argparse

import oauth2 as oauth
import simplejson as json
import httplib

import os

from random import choice


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
def parseBlogData(blogList, apiKey):

    finalData = []

    con = httplib.HTTPConnection('api.tumblr.com')

    for blog in blogList:
        blogurl = blog['url']
# Cut off leading http://
        req_url = '/v2/blog/' + blogurl[7:] + '/posts/photo'
        query = req_url + '?api_key=' + apiKey
        con.request('GET', query)
        r1 = con.getresponse()

        info = json.loads(r1.read())
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
    consumer_key    = config.get('consumer', 'key')
    consumer_secret = config.get('consumer', 'secret')
    oauth_token     = config.get('oauth', 'key')
    oauth_secret    = config.get('oauth', 'secret')

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    token = oauth.Token(oauth_token, oauth_secret)
    client = oauth.Client(consumer, token)

    response, content = client.request('http://api.tumblr.com/v2/user/following', method='POST')

    data = json.loads(content)

    blogData = data['response']['blogs']

    allData =  parseBlogData(blogData, consumer_key)

    print(getPhoto(allData))


if __name__ == '__main__':
    main()

