import json
import configparser
import datetime
import os
import glob
import traceback
from tweepy import OAuthHandler
from tweepy import Stream
from pathlib import Path
from streamer.TwitterStreamer import TweetStreamListener
from streamer.TwitterDbStreamer import TweetDbStreamListener

filterwords=[]
filterlang=[]

config = configparser.ConfigParser()

config.read("./config/TwitterCred.ini")
api_key =config['Twitter']['api_key']
api_secret_key =config['Twitter']['api_secret_key']
access_token =config['Twitter']['access_token']
access_secret_token =config['Twitter']['access_secret_token']

config.read("./config/TReaderConfig.ini")
batch_size=config['Data']['batch_size']
mode=config['Data']['mode']

for key in config['Filter']: 
    filterwords.append(config['Filter'][key])

for key in config['Languages']: 
    filterlang.append(config['Languages'][key])
tweet_count=0
file_count=0
file_counter=0 
path =config['Data']['path']
filesize =config['Data']['filesize']

if __name__ == '__main__':
    if mode=='online':
        try:
            tweetlis = TweetDbStreamListener(int(batch_size))
            auth = OAuthHandler(api_key, api_secret_key)
            auth.set_access_token(access_token, access_secret_token)
            stream = Stream(auth, tweetlis)
            stream.filter(languages=filterlang, track=filterwords)
        except KeyboardInterrupt:
            stream.disconnect()
            print("Capture stopped")
            quit(0)
        except:
            stream.disconnect()
            traceback.print_exc()
            print("Error found")
            quit(1) 
    else:
        try:        
            filename ="tweets_"+str(datetime.date.today().strftime("%Y%m%d"))+"_"
            filename +=  str(file_counter).zfill(5)
            clean_files =  glob.glob(path+'/*.load')
            for clean_file in clean_files:
                print("Removing file {0}",format(clean_file))
                os.remove(clean_file)

            tweet_file = Path(path+"/"+filename+".json")                    
            while tweet_file.is_file():
                print ("File {0} found".format(path+"/"+filename+".json"))
                filename ="tweets_"+str(datetime.date.today().strftime("%Y%m%d"))+"_"
                file_counter += 1
                filename +=  str(file_counter).zfill(5)
                tweet_file = Path(path+"/"+filename+".json")
                
            print("Skipping to file {0}".format(str(file_counter).zfill(5)))
            tweetlis = TweetStreamListener(path,int(filesize),file_counter)
            auth = OAuthHandler(api_key, api_secret_key)
            auth.set_access_token(access_token, access_secret_token)
            stream = Stream(auth, tweetlis)
            stream.filter(languages=filterlang, track=filterwords)
        except KeyboardInterrupt:
            stream.disconnect()

            clean_files =  glob.glob(path+'/*.load')
            for clean_file in clean_files:
                print("Removing file {0}",format(clean_file))
                os.remove(clean_file)

            print("Capture stopped")
            quit(0)
        except:
            stream.disconnect()
            traceback.print_exc()
            print("Error found")
            quit(1)