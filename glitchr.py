#!/usr/bin/env python
# -- coding: utf-8 --

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import ConfigParser
import argparse

import os
import sys

from random import choice
from string import Template

from tumblpy import Tumblpy
from photo import Photo
from jpegglitcher import JpegGlitcher

def parseArgs():
    parser = argparse.ArgumentParser(description='Retrieve Photo Posts')
    parser.add_argument('config', help='The config file')
    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args.config)

    return config

def parseBlogPhotos(blog):
    allPhotos = []

    blogName = blog['blog']['title']
    blogUrl  = blog['blog']['url']

    for post in blog['posts']:

        postUrl  = post['post_url']
        postDate = post['date']

        for photo in post['photos']:

            imgUrl    = photo['original_size']['url']
            name, ext = os.path.splitext(imgUrl)

            # We only want jpeg images, because that's all I can glitch
            if ext == '.jpg' or ext == '.jpeg':
                data = {}
                data['blogName'] = blogName
                data['postUrl']  = postUrl
                data['blogUrl']  = blogUrl
                data['imgUrl']   = imgUrl
                data['postDate'] = postDate
                allPhotos.append(data)

    return allPhotos


# Go through parsing the response for each blog
def getFollowerPhotos(followers, tumblr):

    followerPhotos = []

    for blog in followers:

        blogUrl = blog['url']
        params = {}
        params['tag'] = 'landscape'
        response = tumblr.api_request('posts',
                                      blogUrl,
                                      extra_endpoints=['photo'],
                                      params=params)

        blogName = response['blog']['title']
        photos   = parseBlogPhotos(response)
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
    data['blogName']  = image['blogName']
    data['postUrl']   = image['postUrl']
    data['blogUrl']   = image['blogUrl']
    data['postDate']  = image['postDate']
    data['imgUrl']    = image['imgUrl']
    data['imageData'] = Photo(image['imgUrl'])
    return data

def createCaption(data):
    templt  = '<a href="$imgUrl">Original</a>'
    templt += ' image courtesy of '
    templt += '<a href="${blogUrl}">${blogName}</a>'
    templt += '\n'
    templt += '<a href="$postUrl">First posted</a>'
    templt += ' on ${postDate}'
    c = Template(templt)

    return c.substitute(data)


def main():

    config = parseArgs()
    consumerKey    = config.get('consumer', 'key')
    consumerSecret = config.get('consumer', 'secret')
    oauthToken     = config.get('oauth', 'key')
    oauthSecret    = config.get('oauth', 'secret')

    tumblr = Tumblpy(consumerKey, consumerSecret, oauthToken, oauthSecret)

    data = tumblr.api_request('user/following')

    followers = data['blogs']

    allData =  getFollowerPhotos(followers, tumblr)

    randImage = getRandomPhoto(allData)

    print(randImage)

    randImage['imageData'].retrieve()
    imgData = randImage['imageData'].getData()

    caption = createCaption(randImage)
    print(caption)

    parser = JpegGlitcher(imgData)
    parser.parse_data()
    parser.find_parts()
    parser.quantize_glitch()
    glitched = parser.output_file('output.jpg')
    glitched.name = 'file.jpeg'

    params = {}
    params['type'] = 'photo'
    params['caption'] = caption
    params['tags'] = 'glitch, generative, random'

    #response = tumblr.post('post', 'http://rumblesan.tumblr.com', params=params, files=glitched)
    #print('post id is %s' % response['id'])




if __name__ == '__main__':
    main()

