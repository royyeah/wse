IN4252 Assignments
===

This project contains my code for the assignments to complete the TU Delft course *IN4252 Web, Science and Engineering*.

* **twitter_weka_assignment**: Data mining exercise to retrieve a large random sample from the Twitter stream and do data analysis on what features have predictive value for estimating whether a tweet gets retweeted. I implemented the scripts in Python. The complete [assignment description][3] can also be found in the folder.
 * **SampleDownloader**: Script to listen to Twitter stream for a specified amount of minutes and write output to a file.
 * **SampleUpdater**: Script which checks whether a tweet from the sample is retweeted and updates the output file.
 * **SampleReformatter**: Script that extracts useful features for data analysis, adjusts to a propers scale and writes everything to a CSV file. This file is easily converted to an ARFF file that can be used for doing data analysis using WEKA.
 * **SQLReformatter**: Same script as above, only uses a MySQL database as input, instead of raw JSON stored in a file.
* **recommender_assignment**: Data mining exercise to build a user profile and recommend tweets of others to the concerning user. The complete [assignment description][4] can also be found in the folder.
 * **UserProfileGenerator**: Script that outputs user profiles for a given set of users. The user profile is build by inferring the interest of a user given the user's tweets.  I implemented the scripts in Python.
 * **Recommender**: Script that outputs recommendations for a given set of users. The recommendation is done (1) by depicting the tweets in the same vector space as the user profile and (2) calculating the cosine similarity of the tweets with the user profile.

### Requirements

Python 2.7.x should be installed and I made use of the packages below. Packages can be easily installed using [pip][1]. MySQLdb can't be installed using pip, but the windows binaries can also be found at the same [site][2].

* twitter\_weka\_assignment
 * langid
 * tweepy
* recommender\_assignment
 * calais (from [here][5])
 * numpy
 * sklearn 

[1]: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip
[2]: http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python
[3]: https://github.com/royyeah/wse/blob/master/twitter_weka_assignment/wse-2013-assignment-nov-19.pdf?raw=true
[4]: https://github.com/royyeah/wse/blob/master/recommender_assignment/wse-2013-assignment-dec-02.pdf?raw=true
[5]: https://code.google.com/p/python-calais/
