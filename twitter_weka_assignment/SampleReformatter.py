# Copyright 2013 Roy van der Valk, see LICENSE for details

import json, csv, re, datetime

from tweepy import API
from tweepy.models import Status

# READ FILE
json_inputFile = open('UpdatedSample-2.json', 'r')
data = json.loads(json_inputFile.read())
json_inputFile.close()

# ERRORS
error_list_tweet_ids = []

# TWEET COUNTERS
tweets_discarded_error = 0
tweets_discarded_retweet = 0
tweets_considered = 0

# FEATURE COUNTERS
tweets_username = 0
tweets_hashtag = 0
tweets_url = 0
tweets_question = 0
tweets_exclamation = 0
tweets_pos_term = 0
tweets_neg_term = 0
tweets_pos_emoticon = 0
tweets_neg_emoticon = 0
tweets_reply = 0
tweets_moment_morning = 0
tweets_moment_afternoon = 0
tweets_moment_evening = 0
tweets_moment_night = 0
tweets_retweeted = 0

# REGULAR EXPRESSION PATTERNS
regex_username = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z_]+[A-Za-z0-9_]+)') #http://stackoverflow.com/questions/2304632/regex-for-twitter-username
regex_hashtag = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z_]+[A-Za-z0-9_]+)') #http://stackoverflow.com/questions/2304632/regex-for-twitter-username
regex_url = re.compile(r'(http://[^ ]+)') #http://stackoverflow.com/questions/720113/find-hyperlinks-in-text-using-python-twitter-related

# TERMS & EMOTICONS (Naveed et al.)
positive_terms = ['great', 'like', 'excellent', 'rock on'] 
negative_terms = ['f**k', 'suck', 'fail', 'eww']
positive_emoticons = [':-)', ':)', ';-)', ';)']
negative_emoticons = [':-(', ':(']

# OUTPUT
output = csv.writer(open("output-reformatted.csv", "wb+"))

# API
api = API()

for tweet in data:
    username = 0
    hashtag = 0
    url = 0
    question = 0
    exclamation = 0
    pos_term = 0
    neg_term = 0
    pos_emoticon = 0
    neg_emoticon = 0
    reply = 0
    moment_morning = 0
    moment_afternoon = 0
    moment_evening = 0
    moment_night = 0
    retweeted = 0
    
    status = Status.parse(api, tweet)
    
    if tweet['id'] in error_list_tweet_ids:
        tweets_discarded_error += 1
    elif tweet['text'].startswith("RT @"):
        tweets_discarded_retweet += 1     
    else:
        tweets_considered += 1
        if regex_username.search(tweet['text']) != None:
            tweets_username += 1
            username = 1
        if regex_hashtag.search(tweet['text']) != None:
            tweets_hashtag += 1
            hashtag = 1
        if regex_url.search(tweet['text']) != None:
            tweets_url += 1
            url = 1
        if tweet['text'].find('?') < 0:
            tweets_question += 1
            question = 1
        if tweet['text'].find('!') < 0:
            tweets_exclamation += 1
            exclamation = 1
        if any(term in tweet['text'] for term in positive_terms):
            tweets_pos_term += 1
            pos_term = 1
        if any(term in tweet['text'] for term in negative_terms):
            tweets_neg_term += 1
            neg_term = 1
        if any(emoticon in tweet['text'] for emoticon in positive_emoticons):
            tweets_pos_emoticon += 1
            pos_emoticon = 1
        if any(emoticon in tweet['text'] for emoticon in negative_emoticons):
            tweets_neg_emoticon += 1
            neg_emoticon = 1
        if tweet['in_reply_to_status_id'] != None:
            tweets_reply += 1
            reply = 1 
        timezone_offset = status.user.utc_offset
        if status.user.utc_offset == None:
            status.user.utc_offset = 0
        local_created_at = status.created_at + datetime.timedelta(hours=status.user.utc_offset / 3600)
        if local_created_at.hour < 6:
            tweets_moment_night += 1
            moment_night = 1
        if local_created_at.hour > 6 and local_created_at.hour < 12:
            tweets_moment_morning += 1
            moment_morning = 1
        if local_created_at.hour > 12 and local_created_at.hour < 18:
            tweets_moment_afternoon += 1
            moment_afternoon = 1
        if local_created_at.hour > 18:
            tweets_moment_evening += 1
            moment_evening = 1
        if status.retweet_count > 0:
            tweets_retweeted += 1
            retweeted = 1
            
        output.writerow([username, hashtag, url, question, exclamation, pos_term, neg_term, pos_emoticon, neg_emoticon, reply, moment_morning, moment_afternoon, moment_evening, moment_night, status.user.followers_count, status.user.friends_count, status.user.statuses_count, retweeted])

print "Results:\n"
print "tweets_discarded_error: " + str(tweets_discarded_error)
print "tweets_discarded_retweet: " + str(tweets_discarded_retweet)
print "tweets_considered: " + str(tweets_considered)

print "\n\nFeatures found:\n"
print "tweets_username: " + str(tweets_username)
print "tweets_hashtag: " + str(tweets_hashtag)
print "tweets_url: " + str(tweets_url)
print "tweets_question: " + str(tweets_question)
print "tweets_exclamation: " + str(tweets_exclamation)
print "tweets_pos_term: " + str(tweets_pos_term)
print "tweets_neg_term: " + str(tweets_neg_term)
print "tweets_pos_emoticon: " + str(tweets_pos_emoticon)
print "tweets_neg_emoticon: " + str(tweets_neg_emoticon)
print "tweets_reply: " + str(tweets_reply)
print "tweets_moment_morning: " + str(tweets_moment_morning)
print "tweets_moment_afternoon: " + str(tweets_moment_afternoon)
print "tweets_moment_evening: " + str(tweets_moment_evening)
print "tweets_moment_night: " + str(tweets_moment_night)
print "tweets_retweeted: " + str(tweets_retweeted)
