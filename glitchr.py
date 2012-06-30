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


# Get all the photos from blogs you follow photo posts
# Tag arg can be used to filter
def getBlogPhotos(tumblr, tag=None):
    print('Getting photos from blogs you follow')
    allPhotos = []

    following = tumblr.api_request('user/following')
    print('Following %s blogs' % following['total_blogs'])

    for blog in following['blogs']:
        blogUrl  = blog['url']
        blogName = blog['name']
        print('Getting images from %s at %s' %(blogName, blogUrl))
        params = {}
        if tag:
            params['tag'] = tag

        postsInfo = tumblr.api_request('posts',
                                       blogUrl,
                                       extra_endpoints=['photo'],
                                       params=params)
        allPhotos += parseBlogPosts(postsInfo)

    print('%s photos found to choose from' % len(allPhotos))
    return allPhotos

def parseBlogPosts(postsInfo):
    blogPhotos = []

    blog  = postsInfo['blog']
    posts = postsInfo['posts']

    for post in posts:
        blogPhotos += parsePostPhotos(blog, post)

    print('    blog has %s photos' % len(blogPhotos))
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


# Select a random
def getRandomPhoto(photos):
    print('Selecting a random photo')
    photo = choice(photos)
    p = Photo(photo['imgUrl'])
    p.retrieve()
    photo['imageData'] = p.getData()
    return photo

def createCaption(photo):
    templt  = '<a href="$imgUrl">Original</a> '
    templt += 'image courtesy of '
    templt += '<a href="${blogUrl}">${blogName}</a>'
    templt += '\n'
    templt += '<a href="$postUrl">First posted</a> on ${postDate}'
    c = Template(templt)

    return c.substitute(photo)

def photoInfoLogMessage(photo):
    templt  = 'Caption Info:'
    templt += '\n'
    templt += '    Original image courtesy of ${blogName}'
    templt += '\n'
    templt += '    First posted on ${postDate}'
    templt += '\n'
    c = Template(templt)

    print(c.substitute(photo))


def glitchPhoto(photo):
    print('Glitching image')
    parser = JpegGlitcher(photo['imageData'])
    parser.parse_data()
    parser.find_parts()
    parser.quantize_glitch()
    photo['fp'] = parser.output_file('glitched.jpg')
    photo['fp'].name = 'glitched.jpeg'


def main():

    config = parseArgs()
    consumerKey    = config.get('consumer', 'key')
    consumerSecret = config.get('consumer', 'secret')
    oauthToken     = config.get('oauth', 'key')
    oauthSecret    = config.get('oauth', 'secret')

    tumblr = Tumblpy(consumerKey, consumerSecret, oauthToken, oauthSecret)


    tag = 'landscape'
    allPhotos =  getBlogPhotos(tumblr, tag)

    photo = getRandomPhoto(allPhotos)

    params = {
            'type': 'photo',
            'caption': createCaption(photo),
            'tags': 'glitch, generative, random'
            }

    glitchPhoto(photo)

    response = tumblr.post('post', 'http://rumblesan.tumblr.com', params=params, files=photo['fp'])
    print('post id is %s' % response['id'])


if __name__ == '__main__':
    main()

