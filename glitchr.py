#!/usr/bin/env python
# -- coding: utf-8 --

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import ConfigParser
import argparse

import os
from time import sleep
from basiccache import BasicCache
from datetime import datetime
import sys

from random import choice
from string import Template

from tumblpy import Tumblpy
from photo import Photo
from glitchpy import JpegGlitcher

def parseArgs():
    parser = argparse.ArgumentParser(description='Retrieve Photo Posts')
    parser.add_argument('config', help='The config file')
    parser.add_argument('blogs', help='A file of blogs to search')
    parser.add_argument('-t', '--testing',
                        action='store_true',
                        help="Testing flag. Glitchr won't post photo")
    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args.config)

    return (args, config)


# Get all the photos from blogs you follow photo posts
# Tag arg can be used to filter
def getBlogPhotos(tumblr, blogs, cache, tag=None):
    print('Getting photos from blogs in list')
    allPhotos = []

    for blogUrl in blogs:
        blogInfo = tumblr.api_request('info', blogUrl)['blog']
        blogName = blogInfo['name']
        lastChanged = blogInfo['updated']

        print('    Getting images from %s at %s' %(blogName, blogUrl))
        if cache.hasDataChanged(blogName, lastChanged):
            print('    Querying Tumblr')
            params = {}
            if tag:
                params['tag'] = tag

            postsInfo = tumblr.api_request('posts',
                                           blogUrl,
                                           extra_endpoints=['photo'],
                                           params=params)
            blogPhotos = parseBlogPosts(postsInfo)

            cache.cacheData(blogName, blogPhotos, lastChanged)
        else:
            print('    Using data from cache')
            blogPhotos = cache.retrieveData(blogName)

        allPhotos += blogPhotos

    print('%s photos found to choose from\n' % len(allPhotos))
    return allPhotos

def parseBlogPosts(postsInfo):
    blogPhotos = []

    blog  = postsInfo['blog']
    posts = postsInfo['posts']

    for post in posts:
        blogPhotos += parsePostPhotos(blog, post)

    print('        blog has %s photos' % len(blogPhotos))
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

def printPhotoInfoLogMessage(photo):
    templt  = 'Caption Info:'
    templt += '\n'
    templt += '    Original image courtesy of ${blogName}'
    templt += '\n'
    templt += '    First posted on ${postDate}'
    templt += '\n'
    c = Template(templt)

    print(c.substitute(photo))


def glitchPhoto(photo):
    print('Glitching image\n')
    parser = JpegGlitcher(photo['imageData'])
    parser.parse_data()
    parser.find_parts()
    parser.quantize_glitch()
    photo['fp'] = parser.output_file('glitched.jpg')


def main():

    print('###################')
    print('#     Glitchr     #')
    print('###################')
    print('\n')
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    args, config = parseArgs()
    consumerKey    = config.get('consumer', 'key')
    consumerSecret = config.get('consumer', 'secret')
    oauthToken     = config.get('oauth', 'key')
    oauthSecret    = config.get('oauth', 'secret')


    print('Sorting out Tumblr OAuth')
    tumblr = Tumblpy(consumerKey, consumerSecret, oauthToken, oauthSecret)

    tags = config.get('misc', 'tags').split(',')
    if tags:
        tag = choice(tags)
    else:
        tag = None

    print('Getting images with %s tag' % tag)

    cacheFileName = '%s-%s' % (config.get('cache', 'posts'), tag)
    postCache = BasicCache(cacheFileName)
    postCache.loadCache()

    blogs = open(args.blogs).read().splitlines()
    print('Searching %d blogs' % len(blogs))

    allPhotos =  getBlogPhotos(tumblr, blogs, postCache, tag)

    postCache.saveCache()

    print('Sleeping for a few seconds')
    print('This seems to stop errors with posting the image\n')
    sleep(5)

    photo = getRandomPhoto(allPhotos)
    printPhotoInfoLogMessage(photo)

    params = {
            'type': 'photo',
            'caption': createCaption(photo),
            'tags': 'glitch, generative, random'
            }

    glitchPhoto(photo)

    if args.testing:
        print('Only testing, not posting images')
    else:
        try:
            resp = tumblr.post('post',
                               'http://rumblesan.tumblr.com',
                               params=params,
                               files=photo['fp'])
            # Print a URL to the post we just made
            print('Image posted:')
            print('    http://rumblesan.tumblr.com/post/%s' % resp['id'])
        except AttributeError as e:
            print('Bugger, something went wrong!')
            print(e)

    print('\n')
    print('###################')
    print('#    All done!    #')
    print('###################')
    print('\n\n')



if __name__ == '__main__':
    main()

