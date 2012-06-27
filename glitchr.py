#!/usr/bin/env python

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import ConfigParser
import argparse

import os

from random import choice

from tumblr import Tumblr
from photo import Photo
from jpegglitcher import JpegGlitcher

def parseArgs():
    parser = argparse.ArgumentParser(description='Retrieve Photo Posts')
    parser.add_argument('config', help='The config file')
    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args.config)

    return config

def parseBlogPhotos(posts):
    allPhotos = []
    for post in posts:
        url    = post['post_url']
        date   = post['date']
        photos = post['photos']
        for photo in photos:
            url = photo['original_size']['url']
            name, ext = os.path.splitext(url)

            # We only want jpeg images, because that's all I can glitch
            if ext == '.jpg' or ext == '.jpeg':
                data = {}
                data['url']   = url
                data['date']  = date
                allPhotos.append(data)

    return allPhotos


# Go through parsing the response for each blog
def getFollowerPhotos(followers, tumblr):

    followerPhotos = []

    for blog in followers:

        blogUrl = blog['url']
        # Cut off leading 'http://'
        posts = tumblr.getPosts(blogUrl[7:], 'photo')

        if posts['meta']['status'] != 200:
            print('could not get posts for %s' % blogUrl)
        else:
            response = posts['response']
            blogName = response['blog']['title']
            posts    = response['posts']
            photos   = parseBlogPhotos(posts)
            if photos:
                blogData = {}
                blogData['name']   = blogName
                blogData['url']    = blogUrl
                blogData['photos'] = photos
                followerPhotos.append(blogData)

    return followerPhotos

def getRandomPhoto(data):
    blog = choice(data)
    image = choice(blog['photos'])
    data = {}
    data['name']  = blog['name']
    data['url']   = blog['url']
    data['image'] = image['url']
    data['date']  = image['date']
    data['imageData'] = Photo(data['image'])
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

    randImage = getRandomPhoto(allData)

    randImage['imageData'].retrieve()
    randImage['imageData'].save('temp.jpg')

    parser = JpegGlitcher('temp.jpg')
    parser.parse_file()
    parser.find_parts()
    parser.quantize_glitch()
    parser.output_file('output.jpg')



if __name__ == '__main__':
    main()

