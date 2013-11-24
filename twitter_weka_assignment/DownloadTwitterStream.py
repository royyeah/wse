'''
Created on 24 nov. 2013

@author: royyeah
'''

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import config, time, sys

class StreamDownloader(StreamListener):
    """ 
    A downloader which saves tweets received from the stream to a sample.json file.
    > Duration in minutes
    """
    def __init__(self, duration):
        self.counter = 0
        self.started = time.time()
        self.duration = duration*60
        self.output = open('sample.json', 'w+')
    
    def on_data(self, data):
        if time.time() >= self.started + self.duration:
            print "================= STATISTICS ================="
            print "Start time (seconds since the Epoch): " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.started))
            print "End time (seconds since the Epoch): " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print "Tweets downloaded: " + str(self.counter)
            sys.exit()
        else:
            self.output.write(data)
            self.counter += 1
            return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    downloader = StreamDownloader(10)
    auth = OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)
    
    stream = Stream(auth, downloader)
    stream.sample() 