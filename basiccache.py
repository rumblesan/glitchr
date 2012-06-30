#!/usr/bin/env python

import pickle

class BasicCache(object):

    def __init__(self, cacheFile):
        self.filename = cacheFile + '.bch'
        self.cache = {}

    def loadCache(self):
        fp = open(self.filename)
        self.cache = pickle.load(fp)
        fp.close()

    def saveCache(self):
        fp = open(self.filename, 'w')
        pickle.dump(self.cache, fp)
        fp.close()

    def cacheData(self, key, data, timestamp=0):
        self.cache[key] = {
                'timestamp': timestamp,
                'data': data
                }

    def dataExists(self, key):
        return key in self.cache

    def hasDataChanged(self, key, timestamp):
        if self.dataExists(key):
            return timestamp > self.cache[key]['timestamp']
        else:
            return True

    def retrieveData(self, key):
        if self.dataExists(key):
            return self.cache[key]['data']
        else:
            return None

