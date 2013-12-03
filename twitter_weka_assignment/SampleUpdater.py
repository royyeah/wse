# Copyright 2013 Roy van der Valk, see LICENSE for details

import json, time, config

from tweepy import OAuthHandler
from tweepy import API
from tweepy.error import TweepError

# SETTINGS
max_tweets_per_hour = 720
save_at = 100
safety_buffer_sec = 0.02
search = False
start_at = 0
update_list = False
tweet_list = []

wait_per_request = 3600.0 / max_tweets_per_hour + safety_buffer_sec

# READ FILE
json_file = open('UpdatedSample.json', 'r')
data = json.loads(json_file.read())
json_file.close()

auth = OAuthHandler(config.twitter_consumer_key, config.twitter_consumer_secret)
auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)

api = API(auth)

started = time.time()

counter = 0
counter_break = 0
counter_skip = 0
counter_skip_break = 0
error_counter = {}
error_ids = []
found = False

print "Starting...\n"

for tweet in data:
    # Search for tweet in JSON
    if search:
        if tweet['id'] == start_at:
            search = False
            print "Found tweet " + str(start_at) + ", starting here...\n"
            continue
        continue   
    
    try:
        if update_list:
            if tweet['id'] in tweet_list:
                counter += 1
                counter_break += 1
                status = api.get_status(tweet['id'])
                tweet['retweet_count'] = status.retweet_count
                time.sleep(wait_per_request)
            else:
                counter_skip += 1
                counter_skip_break += 1
                if counter_skip_break == 100:
                    counter_skip_break = 0
                    print "Skipped a " + str(counter_skip) + "..."
        else:
            counter += 1
            counter_break += 1
            status = api.get_status(tweet['id'])
            tweet['retweet_count'] = status.retweet_count
            time.sleep(wait_per_request)
    except TweepError as e:
        reason = str(e.reason)
        if reason in error_counter:
            error_counter[reason] += 1
        else:
            error_counter[reason] = 1
        error_ids.append(tweet['id'])
        time.sleep(wait_per_request)
    if counter_break == save_at:
        print "Saved at " + str(counter) + " tweets crawled..."
        print "=========== INTERMEDIATE RESULT ==========="
        print "==== BEGIN ERROR ===="
        print error_counter
        print error_ids
        print "==== END ERROR ===="
        ended = time.time()
        totaltime = ended - started
        print "Start time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(started))
        print "End time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ended))
        print "Total time: " + str(totaltime) + " seconds \n"
        json_tmpFile = open('output-{0}.json'.format(tweet['id']), 'w+')
        json_tmpFile.write(json.dumps(data))
        json_tmpFile.close()
        counter_break = 0
            
print "Saved at " + str(counter) + " tweets crawled..."
print "=========== END RESULT ==========="
print "==== BEGIN ERROR ===="
print error_counter
print error_ids
print "==== END ERROR ===="
ended = time.time()
totaltime = ended - started
print "Start time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(started))
print "End time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ended))
print "Total time: " + str(totaltime) + " seconds \n"

json_newFile = open('output-final.json', 'w+')
json_newFile.write(json.dumps(data))