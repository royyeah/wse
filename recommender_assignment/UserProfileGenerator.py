# Copyright 2013 Roy van der Valk, see LICENSE for details

import MySQLdb, time, config
from calais import Calais

# Settings
usernames = []
limit = None
wait_per_request = 0.251 # Rate limit of Calais is 4 transactions per sec, 50,000 per day

# Configure DB
db = MySQLdb.connect(host=config.mysql_host,
                     user=config.mysql_user,
                     passwd=config.mysql_passwd,
                     db='assignment2')
cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS tweet_topic")
cursor.execute("DROP TABLE IF EXISTS tweet_entity")
cursor.execute("""CREATE TABLE tweet_topic
(
ID int NOT NULL AUTO_INCREMENT,
tweet_id bigint(20) NOT NULL,
topic varchar(255) NOT NULL,
score float NOT NULL,
PRIMARY KEY (ID)
);""")
cursor.execute("""CREATE TABLE tweet_entity
(
ID int NOT NULL AUTO_INCREMENT,
tweet_id bigint(20) NOT NULL,
entity varchar(255) NOT NULL,
relevance float NOT NULL,
PRIMARY KEY (ID)
);""")
q_topic_insert = "INSERT INTO tweet_topic (tweet_id,topic,score) VALUES (%s,%s,%s);"
q_entity_insert = "INSERT INTO tweet_entity (tweet_id,entity,relevance) VALUES (%s,%s,%s);"

# Configure Calais connection
calais = Calais(config.calais_api_key, submitter=config.calais_user)

userprofiles = {}
last_time = time.time()

for username in usernames:
    if limit == None:
        cursor.execute("SELECT id, content FROM tweets_sample WHERE username='" + username + "'")
    else:
        cursor.execute("SELECT id, content FROM tweets_sample WHERE username='" + username + "' LIMIT " + str(limit))
    data = cursor.fetchall()
    
    analyzed = 0
    skipped = 0
    topics = {}
    no_topics = 0
    named_entities = {}
    no_named_entities = 0
    
    for tweet in data:
        try:
            analyzed += 1
            
            # Wait until wait time is passed and let Calais analyze a new tweet
            time_passed = time.time() - last_time
            wait_time = max(wait_per_request - time_passed, 0)
            time.sleep(wait_time)   
            result = calais.analyze(tweet[1])
            last_time = time.time()
            
            # Extract entities
            try:
                for entity in result.entities:
                    name = entity["name"]
                    if (name == u'RT') | (entity["_type"] == u'URL'):
                        continue
                    cursor.execute(q_entity_insert, (str(tweet[0]), name, str(entity["relevance"])))
                    db.commit()
                    if name in named_entities:
                        named_entities[name] += 1
                    else:
                        named_entities[name] = 1
            except AttributeError:
                no_named_entities += 1
            
            # Extract topics
            try:
                for topic in result.topics:
                    name = topic["categoryName"]
                    cursor.execute(q_topic_insert, (str(tweet[0]), name, str(topic["score"])))
                    db.commit()
                    if name in topics:
                        topics[name] += 1
                    else:
                        topics[name] = 1
            except AttributeError:
                no_topics += 1
        except ValueError:
            skipped += 1
    
    user = {}
    vector_sum = sum(topics.itervalues())
    for topic in topics:
        user[topic] = float(topics[topic])/vector_sum
    userprofiles[username] = user    
    
    print "==== User info for " + username + " ===="
    print "TOPICS:"
    print topics
    print "\nENTITIES:"
    print named_entities
    print "\nUSER PROFILE:"
    print user
    print "\nSCRIPT SUMMARY:"
    print "Analyzed tweets: " + str(analyzed)
    print "Tweets with no entities: " + str(no_named_entities)
    print "Tweets with no topics: " + str(no_topics)
    print "Skipped tweets: " + str(skipped)
    print "==== End user info ====\n\n"
 
db.close()

print "==== USER PROFILES ===="
print userprofiles        