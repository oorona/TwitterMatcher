import json
from tweepy.streaming import StreamListener
from streamer.StreamCleaner import StreamCleaner

class TweetDbStreamListener(StreamListener):
    tweet_count=0

    def __init__(self,batch_size,keep_batch):
        StreamListener.__init__(self,api=None)
        self.loader = StreamCleaner(batch_size,keep_batch)
        
    def on_data(self, data):
        tweet = json.loads(data)
        self.loader.loadTweet(tweet)
        self.tweet_count+=1
        try:
            print ("Tweets {0}/{1} batch {2} lang {3} text={4}".format(self.loader.total_tweets,self.tweet_count,self.loader.batch_counter,tweet["lang"],tweet["text"]))
        except KeyError:
            pass
        return True

    def on_error(self, status):
        print (status)         
        if status == 420:
            return False

    def on_status(self, status):
        print(status.text)