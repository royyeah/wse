# Copyright 2013 Roy van der Valk, see LICENSE for details

import config, time, langid

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy.models import Status

from tweepy.utils import import_simplejson
json = import_simplejson()

class StreamDownloader(StreamListener):
    """ 
    A downloader which saves tweets received from the stream to a sample.json file.
    > Duration in minutes
    > Language in ISO 639-1 code
    """
    def __init__(self, duration, lang, lang_threshold):
        self.api = API()
        self.lang = lang
        self.lang_threshold = lang_threshold
        self.counter = {lang + '-above':0, lang + '-below':0, 'excluded':0}
        self.started = time.time()
        self.duration = 10
        self.first_tweet_id = ''
        self.last_tweet_id = ''
        self.above_output = open('{0}-sample-above-{1}.json'.format(int(self.started), self.lang), 'w+')
        self.below_output = open('{0}-sample-below-{1}.json'.format(int(self.started), self.lang), 'w+')
        self.excl_output = open('{0}-sample-excluded.json'.format(int(self.started)), 'w+')
    
    def on_data(self, data):
        if time.time() >= self.started + self.duration:
            stats = open('{0}-sample.stats'.format(int(self.started)), 'w+')
            stats.write("================= STATISTICS =================" + "\n")
            stats.write("Start time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.started)) + "\n")
            stats.write("End time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + "\n")
            stats.write("First Tweet ID: " + self.first_tweet_id + "\n")
            stats.write("Last Tweet ID: " + self.last_tweet_id + "\n")
            stats.write("Language: " + self.lang + "\n")
            stats.write("Language classification threshold: " + str(self.lang_threshold) + "\n")
            stats.write("Above threshold: " + str(self.counter[self.lang + '-above']) + "\n")
            stats.write("Below threshold: " + str(self.counter[self.lang + '-below']) + "\n")
            stats.write("Exluded: " + str(self.counter['excluded']) + "\n")
            return False
        elif 'in_reply_to_status_id' in data: 
            status = Status.parse(self.api, json.loads(data))
            langclass = langid.classify(status.text)
            
            if (self.counter == {self.lang + '-above':0, self.lang + '-below':0, 'excluded':0}):
                self.first_tweet_id = str(status.id)
            self.last_tweet_id = str(status.id)
            
            if (langclass[0] == self.lang):                
                if langclass[1] >= self.lang_threshold:
                    self.above_output.write(data)
                    self.counter[self.lang + '-above'] += 1
                else:
                    self.below_output.write(data)
                    self.counter[self.lang + '-below'] += 1
            else:
                self.excl_output.write(data)
                self.counter['excluded'] += 1
               
            return True

if __name__ == '__main__':
    downloader = StreamDownloader(duration = 10, 
                                  lang = 'en', 
                                  lang_threshold = 0.9)
    
    auth = OAuthHandler(config.twitter_consumer_key, config.twitter_consumer_secret)
    auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)
    
    stream = Stream(auth, downloader)
    stream.sample() 