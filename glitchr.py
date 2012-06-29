#!/usr/bin/env python
# -- coding: utf-8 --

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import ConfigParser
import argparse

import os

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


# Get all the photos from followers photo posts
def getFollowerPhotos(followers, tumblr, tag=None):
    allPhotos = []

    for blog in followers:
        blogUrl = blog['url']
        params = {}
        if tag:
            params['tag'] = tag

        postsInfo = tumblr.api_request('posts',
                                       blogUrl,
                                       extra_endpoints=['photo'],
                                       params=params)
        allPhotos += parseFollowerPosts(postsInfo)

    return allPhotos

def parseFollowerPosts(postsInfo):
    blogPhotos = []

    blog  = postsInfo['blog']
    posts = postsInfo['posts']

    for post in posts:
        blogPhotos += parsePostPhotos(blog, post)

    return blogPhotos

def parsePostPhotos(blog, post):
    postPhotos = []

    blogName = blog['title']
    blogUrl  = blog['url']

    postUrl  = post['post_url']
    postDate = post['date']
    photos   = post['photos']

    # There could be multiple photos in one post
    # so we need to iterate through them all
    for photo in photos:
        imgUrl = photo['original_size']['url']
        name, ext = os.path.splitext(imgUrl)

        # We only want jpeg images, because that's all we can glitch atm
        if ext == '.jpg' or ext == '.jpeg':
            data = {
                    'blogName': blogName,
                    'postUrl': postUrl,
                    'blogUrl': blogUrl,
                    'imgUrl': imgUrl,
                    'postDate': postDate
                    }
            postPhotos.append(data)

    return postPhotos



def getRandomPhoto(photos):
    photo = choice(photos)
    photo['imageData'] = Photo(photo['imgUrl'])
    return photo

def createCaption(data):
    templt  = '<a href="$imgUrl">Original</a> '
    templt += 'image courtesy of '
    templt += '<a href="${blogUrl}">${blogName}</a>'
    templt += '\n'
    templt += '<a href="$postUrl">First posted</a> on ${postDate}'
    c = Template(templt)

    return c.substitute(data)


def main():

    config = parseArgs()
    consumerKey    = config.get('consumer', 'key')
    consumerSecret = config.get('consumer', 'secret')
    oauthToken     = config.get('oauth', 'key')
    oauthSecret    = config.get('oauth', 'secret')

    tumblr = Tumblpy(consumerKey, consumerSecret, oauthToken, oauthSecret)

    followers = tumblr.api_request('user/following')['blogs']

    tag = 'landscape'
    allPhotos =  getFollowerPhotos(followers, tumblr, tag)

    print('%s photos found to choose from' % len(allPhotos))

    photo = getRandomPhoto(allPhotos)

    photo['imageData'].retrieve()
    imgData = photo['imageData'].getData()

    caption = createCaption(photo)
    print(caption)

    parser = JpegGlitcher(imgData)
    parser.parse_data()
    parser.find_parts()
    parser.quantize_glitch()
    glitched = parser.output_file('output.jpg')
    glitched.name = 'file.jpeg'

    params = {
            'type': 'photo',
            'caption': caption,
            'tags': 'glitch, generative, random'
            }

    response = tumblr.post('post', 'http://rumblesan.tumblr.com', params=params, files=glitched)
    print('post id is %s' % response['id'])




if __name__ == '__main__':
    main()

