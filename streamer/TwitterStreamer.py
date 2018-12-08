import os
import json
import datetime
from tweepy.streaming import StreamListener


class TweetStreamListener(StreamListener):
    tweet_count=0
    path=""
    tweet_block_size=0
    file_count=0

    def __init__(self,path,block_size,file_counter):
        StreamListener.__init__(self,api=None)
        self.path=path
        self.tweet_block_size=block_size
        self.file_count=file_counter
        
    def on_data(self, data):
        filename ="tweets_"+str(datetime.date.today().strftime("%Y%m%d"))+"_"
        file_number=str(self.file_count).zfill(5)
        filename += file_number
        
        self.tweet_count += 1  
        with open(self.path+"/"+filename+".json.load","a") as tf:
            tf.write(data)
        
        if (self.tweet_count % self.tweet_block_size) == 0 :
            self.tweet_count=0
            self.file_count +=1
            tf.close
            os.rename(self.path+"/"+filename+".json.load",self.path+"/"+filename+".json")

        data = json.loads(data)
        print ("file {0} tweet {1} lang {2} text={3}".format(file_number,self.tweet_count,data["lang"],data["text"]))
        return True

    def on_error(self, status):
        print (status)         
        if status == 420:
            return False

    def on_status(self, status):
        print(status.text)