import json 
import glob
import re
import string
import sqlite3
import configparser
import datetime
import math
import traceback
import collections
from cleaner.Lemmatizer import Lemmatizer
from cleaner.ContractionExpander import ContractionExpander
from cleaner.StopWorder import StopWorder

class StreamCleaner:
    files_loaded=0
    total_tweets=0
    batch_counter=0
    batch_size=0

    config = configparser.ConfigParser()
    config.read("./config/DbSettings.ini")
    db_file =config['Database']['db_file_name']
    dbconn = sqlite3.connect(db_file)

    tweets_insert =config['Sql']['tweets_insert']
    hashtags_insert =config['Sql']['hashtags_insert']
    urls_insert =config['Sql']['urls_insert']
    usermentions_insert =config['Sql']['usermentions_insert']
    tokens_insert =config['Sql']['tokens_insert']
    tokens_tweets_insert  =config['Sql']['tokens_tweets_insert']
    tokens_update =config['Sql']['tokens_update']
    tokens_select =config['Sql']['tokens_select']
    tweets_select_total =config['Sql']['tweets_select_total']
    tokens_select_all =config['Sql']['tokens_select_all']
    tokens_update_idf =config['Sql']['tokens_update_idf']

    tweets=config['Ddl']['tweets']
    urls=config['Ddl']['urls']
    hashtags=config['Ddl']['hashtags']
    usermentions=config['Ddl']['usermentions']
    tokens=config['Ddl']['tokens']
    tokens_tweets=config['Ddl']['tokens_tweets']
    indexw_t=config['Ddl']['indexw_t']

    transtable = str.maketrans('!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~',"                                ")
    lemma = Lemmatizer()
    cont = ContractionExpander()
    stop = StopWorder()

    def __init__(self,batch_size):
        self.batch_size=batch_size
        self.batch_counter=0

    def removeHashtags(self,text,hashtags):
        for hashtag in hashtags:
            starth=hashtag['indices'][0]
            endh=hashtag['indices'][1]
            blank = " "*(endh-starth)
            text=text[:starth]+blank+text[endh:]
        return text

    def removeUrls(self,text,urls):
        for url in urls:
            starth=url['indices'][0]
            endh=url['indices'][1]
            blank = " "*(endh-starth)
            text=text[:starth]+blank+text[endh:]
        return text    

    def removeUserMentions(self,text,usermentions):
        for usermention in usermentions:
            starth=usermention['indices'][0]
            endh=usermention['indices'][1]
            blank = " "*(endh-starth)
            text=text[:starth]+blank+text[endh:]
        return text       

    def removeUrl(self,text):
        p =re.compile('http[s]?://[\w.]*\w*[/]?\w*')
        for url in p.finditer(text):
            starth=url.start()
            endh=url.end()        
            blank = " "*(endh-starth)
            text=text[:starth]+blank+text[endh:]  
        return text
        
    def removeBlanks(self,text):
        return re.sub(' +', ' ',text)
        
    def makeLowerCase(self,text):
        return text.lower()

    def removePunctuations(self,text):
        return text.translate(self.transtable)
    
    def removeUnicodeSymbols(self,text):
        return re.sub(u"[^\u0000-\u007e]+","",text)

    def removeMultiline(self,text):
        return text.replace('\n',' ')
    
    def removeNumbers(self,text):
        return re.sub("\d+","",text)

    def removePosessives(self,text):
        text= text.replace("'s"," ")
        return  text.replace("\u2019s"," ")
    
    def expandContractions(self, text):
        tokens=text.split()
        con_tokens=[self.cont.expand(t) for t in tokens]
        return ' '.join(con_tokens)

    def tokenize(self,text):
        return text.split()

    def lemmatize(self,tokens):
        return [self.lemma.lemmatize(t) for t in tokens]
  
    def removeStopWords(self,tokens):
        toks=[]
        for t in tokens:
            if not self.stop.isStopWord(t):
               toks.append(t)
        return toks
    
    def removeShortWords(self,tokens):
        toks=[]
        for t in tokens:
            if len(t)>2:
               toks.append(t)
        return toks

    def isRetweeted (self,tweet):
        if "retweeted_status" not in tweet:
            return False
        else:
            return True

    def isExtended (self,tweet):
        if "extended_tweet" not in tweet:
            return False
        else:
            return True        

    def hasUrl(self,text):
        if text.find('http') >= 0:
            return True
        else:
            return False

    def getExtendedText(self,tweet):
        return tweet['extended_tweet']['full_text']

    def getText(self,tweet):
        return tweet['text']

    def getEntities(self,tweet):
        return tweet['entities']

    def getExtendedEntities(self,tweet):
        return tweet['extended_tweet']['entities']
    
    def getEntitiesHashtags(self,entity):
        return entity['hashtags']

    def getEntitiesUrls(self,entity):
        return entity['urls']

    def getEntitiesUserMentions(self,entity):
        return entity['user_mentions']

    def getEntitiesSymbols(self,entity):
        return entity['symbols']

    def insertTweet(self,id,text,origtext):
        cursor = self.dbconn.cursor()
        data = (id,text,origtext,str(datetime.datetime.today()))
        cursor.execute(self.tweets_insert,data)
        
    def insertHashtags(self,id,hashtags):
        cursor = self.dbconn.cursor()
        for hashtag in hashtags:       
            data= (id,hashtag['text'])
            cursor.execute(self.hashtags_insert,data)
        
    def insertUrls(self,id,urls):
        cursor = self.dbconn.cursor()
        for url in urls:           
            data= (id,url['expanded_url'])
            cursor.execute(self.urls_insert,data)
        
    def insertUserMentions(self,id,usermentions):
        cursor = self.dbconn.cursor()
        for usermention in usermentions:           
            data= (id,usermention['id'],usermention['name'],usermention['screen_name'])
            cursor.execute(self.usermentions_insert,data)
        
    def insertTokens(self,id,tokens):
        cursor = self.dbconn.cursor()  
        count_tokens=collections.Counter(tokens)
                
        for token in count_tokens:
            data=(token,token)
            cursor.execute(self.tokens_insert,data)
            
            data=[token,id,count_tokens[token]]
            cursor.execute(self.tokens_tweets_insert,data)

           

    def updateIDF(self):
        cursor = self.dbconn.cursor()
        cursor.execute(self.tweets_select_total)
        result=cursor.fetchone()
        total_tweets=result[0]
        cursor.execute(self.tokens_select_all)
        results=cursor.fetchall()
        for result in results:
            data=(math.log2(total_tweets/result[1]),result[0])
            cursor.execute(self.tokens_update_idf,data)


    def startTransaction(self):
        self.dbconn.execute("PRAGMA foreign_keys = ON")

    def endTransaction(self):
        self.total_tweets +=1

        if self.total_tweets%self.batch_size == 0:
            self.updateIDF()        
            self.dbconn.commit()
            self.batch_counter +=1
            print("Commiting batch {0}. Total Tweets ={1}".format(self.batch_counter,self.total_tweets))

    def loadTweet(self,tweet):
        if not self.isRetweeted(tweet):
            try:
                id=tweet['id']
                if not self.isExtended(tweet):
                    entities=self.getEntities(tweet)
                    text=self.getText(tweet)
                else:
                    entities=self.getExtendedEntities(tweet)
                    text=self.getExtendedText(tweet)
                origtext=text
                text=self.removeHashtags(text,self.getEntitiesHashtags(entities))             
                text=self.removeUrls(text,self.getEntitiesUrls(entities))            
                if self.hasUrl(text):
                    text=self.removeUrl(text)
                text=self.removeUserMentions(text,self.getEntitiesUserMentions(entities))             
                text=self.removeMultiline(text)
                text=self.makeLowerCase(text)
                text=self.removeNumbers(text)
                text=self.expandContractions(text)
                text=self.removePosessives(text)
                text=self.removeUnicodeSymbols(text)
                text=self.removePunctuations(text)
                text=self.removeBlanks(text)
                tokens=self.tokenize(text)
                tokens=self.removeStopWords(tokens)
                tokens=self.lemmatize(tokens)
                tokens=self.removeShortWords(tokens)  
                text=' '.join(tokens)
                self.startTransaction
                self.insertTweet(id,text,origtext)
                self.insertHashtags(id,self.getEntitiesHashtags(entities))
                self.insertUrls(id,self.getEntitiesUrls(entities))
                self.insertUserMentions(id,self.getEntitiesUserMentions(entities))
                self.insertTokens(id,tokens)
                self.endTransaction()
            except sqlite3.IntegrityError:
                print ("###################################################################################")
                pass
            except KeyError:
                print ("###################################################################################")
                pass
            except Exception as dberror:
                traceback.print_exc()
                print('Error inserting tweetid: {0}\nMessage: {1}'.format(id, str(dberror)))
                self.dbconn.rollback()
        

    def loadFile(self,file,last=False):
        self.files_loaded+=1
        print("Opening file {0}".format(file))
        tweets_file = open(file, "r")        
        for line in tweets_file:  
            tweet = json.loads(line)     
            self.loadTweet(tweet)
        if last :
            self.batch_counter +=1
            print("Commiting batch {0}. Total Tweets ={1}".format(self.batch_counter,self.total_tweets))
            self.dbconn.commit()
                
    def loadPath(self,path,format):
        load_files =  glob.glob(path+'/'+format)
        load_files.sort()
        for load_file in load_files:
            print("Processing file {0}".format(load_file))
            self.loadFile(load_file)
        self.batch_counter +=1
        print("Commiting batch {0}. Total Tweets ={1}".format(self.batch_counter,self.total_tweets))
        self.dbconn.commit()
            