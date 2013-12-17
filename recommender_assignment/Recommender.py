# Copyright 2013 Roy van der Valk, see LICENSE for details

import config, MySQLdb, numpy, operator, time
from sklearn.metrics import pairwise_distances 
from calais import Calais

# Configure DB
db = MySQLdb.connect(host=config.mysql_host,
                     user=config.mysql_user,
                     passwd=config.mysql_passwd,
                     db='assignment2')
cursor = db.cursor()

calais = Calais(config.calais_api_key, submitter=config.calais_user)

userprofiles = {}

for user in userprofiles:
    userprofile = userprofiles[user]
    user_vector = userprofile.values()
    cosine_vector = [user_vector]
     
    topics = userprofile.keys()
     
    cursor.execute("SELECT id FROM tweets_sample WHERE username=%s;", (user))
    own_tweet_ids = [item[0] for item in cursor.fetchall()]
     
    placeholder = '%s'
    placeholders_topics = ', '.join(placeholder for unused in topics)
    placeholders_ids = ', '.join(placeholder for unused in own_tweet_ids)
    get_topic_tweets_query = "SELECT tweet_id FROM tweet_topic WHERE topic IN (%s) AND tweet_id NOT IN (%s) GROUP BY tweet_id;" % (placeholders_topics, placeholders_ids)
     
    replacements = topics + own_tweet_ids
    cursor.execute(get_topic_tweets_query, replacements)
    topic_tweet_ids = [item[0] for item in cursor.fetchall()]
     
    for tweet_id in topic_tweet_ids:
        tweet_vector = []
        # Get unnormalized vector
        for topic in topics:
            cursor.execute("SELECT score FROM tweet_topic WHERE tweet_id=%s AND topic=%s", (tweet_id, topic))
            topic_score_list = [item[0] for item in cursor.fetchall()]
            topic_score = 0
            if len(topic_score_list) != 0:
                topic_score = topic_score_list[0]
            tweet_vector.append(topic_score)
        # Normalize vector
        tweet_vector_n = []
        vector_sum = sum(tweet_vector)
        for score in tweet_vector:
            tweet_vector_n.append(float(score)/vector_sum)
        cosine_vector.append(tweet_vector_n)
     
    cosine_vector_numpy = numpy.array(cosine_vector)
    cosine_matrix = 1-pairwise_distances(cosine_vector_numpy, metric="cosine")
    
    print "=== USER REPORT FOR %s ===" % user
    sorted_userprofile = sorted(userprofile.iteritems(), key=operator.itemgetter(1), reverse=True)
    print "User-profile (sorted): " + str(sorted_userprofile)    
    
    # Get top 3 tweets
    for cos_element in cosine_matrix:
        cos_sim_dict = dict(enumerate(cos_element[1:])) # index is correct, because original is not in set of tweet ids
        three_largest = dict(sorted(cos_sim_dict.iteritems(), key=operator.itemgetter(1), reverse=True)[:3])
        for tweet_index in three_largest:
            tweet_id = topic_tweet_ids[tweet_index]
            cursor.execute("SELECT username,content FROM tweets_sample WHERE id=%s;", (tweet_id))
            tweet_f = cursor.fetchall()
            tweet = tweet_f[0]
            time.sleep(0.25)
            c_result = calais.analyze(tweet[1])
            topics = []
            for topic in c_result.topics:
                name = topic["categoryName"]
                topics.append(name)
            topics_str = ', '.join(topics)
            print "User: %s\nTweet-ID: %s\nTweet-Text: %s\nTopics: %s\n" % (tweet[0], tweet_id, tweet[1], topics_str)
        break # only first element, because this is similiarity with user profile 
        
    print "=== END USER REPORT FOR %s ===" % user