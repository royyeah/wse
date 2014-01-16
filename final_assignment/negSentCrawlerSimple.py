# Copyright 2013 Roy van der Valk, see LICENSE for details

import time, config
from tweepy import OAuthHandler
from tweepy import API

# SETTINGS
retweet_threshold = 0
max_tweets_per_hour = 720
save_at = 100
safety_buffer_sec = 0.02
wait_per_request = 3600.0 / max_tweets_per_hour + safety_buffer_sec

# TWITTER CONFIG
auth = OAuthHandler(config.twitter_consumer_key, config.twitter_consumer_secret)
auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)
api = API(auth)

# QUERIES
searchQueriesPerBank = {
    'Bank of America': "(@BofA_Help OR #BankofAmerica OR #BofA OR \"Bank of America\")",
    'Barclays': "@Barclays OR @BarclaysOnline OR #Barclays OR Barclays",
    'Citi': "@Citi OR @AskCiti OR #Citi OR Citi"
}
negSearchQuery = " AND (fail OR fuck OR hate OR poor OR shit OR suck)"

started = time.time()
for bank in searchQueriesPerBank:
    searchQuery = searchQueriesPerBank[bank] + negSearchQuery
    print "> QUERY: " + searchQuery
    max_id = 0
    while True:
        time.sleep(wait_per_request)
        if max_id == 0:
            results = api.search(q = searchQuery, count=100, lang='en')
        else:
            results = api.search(q = searchQuery, max_id=max_id - 1, count=100, lang='en')
        
        if len(results) == 0:
            print "\n\n\n"
            break #Break out of while loop and start with the next bank
        else:
            for result in results:
                max_id = result.id
                if result.retweet_count >= retweet_threshold:
                    print "\n======= TWEET ======="
                    print "ID: " + str(result.id)
                    print "USER: " + str(result.user.name)
                    print "DATE: " + str(result.created_at)
                    print "RETWEETS: " + str(result.retweet_count)
                    print "TEXT: " + str(result.text)