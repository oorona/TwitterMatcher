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
    keep_batch=0

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
    snapshots_insert=config['Sql']['snapshots_insert']
    tweets_delete_older=config['Sql']['tweets_delete_older']
    snapshots_delete_older=config['Sql']['snapshots_delete_older']
    tokens_delete_older=config['Sql']['tokens_delete_older']
    snapshots_select_count_all=config['Sql']['snapshots_select_count_all']
    update_tokens_doc_number=config['Sql']['update_tokens_doc_number']
    tokens_tweets_delete=config['Sql']['tokens_tweets_delete']
    pragma_on=config['Sql']['pragma_on']
    sql_changes=config['Sql']['sql_changes']


    tweets=config['Ddl']['tweets']
    urls=config['Ddl']['urls']
    hashtags=config['Ddl']['hashtags']
    usermentions=config['Ddl']['usermentions']
    tokens=config['Ddl']['tokens']
    tokens_tweets=config['Ddl']['tokens_tweets']
    snapshots=config['Ddl']['snapshots']
    indextt_token_id=config['Ddl']['indextt_token_id']
    indextt_tweet_id=config['Ddl']['indextt_tweet_id']
    indext_c=config['Ddl']['indext_c']

    transtable = str.maketrans('!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~',"                                ")
    lemma = Lemmatizer()
    cont = ContractionExpander()
    stop = StopWorder()

    def __init__(self,batch_size,keep_batch):
        self.create_db()
        self.batch_size=batch_size
        cursor=self.dbconn.cursor()
        cursor.execute(self.snapshots_select_count_all)
        self.batch_counter=cursor.fetchone()[0]+1
        self.keep_batch=keep_batch
        cursor.execute(self.tweets_select_total)
        result=cursor.fetchone()
        self.total_tweets=result[0]
        self.trimData()

    def create_db(self):
        self.create_db_object(self.tweets)
        self.create_db_object(self.urls)
        self.create_db_object(self.hashtags)
        self.create_db_object(self.usermentions)
        self.create_db_object(self.tokens)
        self.create_db_object(self.tokens_tweets)
        self.create_db_object(self.snapshots)
        self.create_db_object(self.indextt_token_id)
        self.create_db_object(self.indextt_tweet_id)
        self.create_db_object(self.indext_c)
    
    def create_db_object(self, ddl):
        try:
            c = self.dbconn.cursor()
            c.execute(ddl)
        except Exception :
            pass
    # @BEGIN TwitterDataCleaning @DESC Workflow for cleaning and loading tweets to database
    # @PARAM path @DESC Provides path location for offline Json files
    # @PARAM format @DESC Provides format of twitter files
    # @IN onlinetweet
    # @IN twitter_file

    
    # @BEGIN LoadTwitterData @DESC Scans and processes all files under folder
    # @IN path  @URI file:{path}/{format}.json
    # @IN format 
    # @OUT file  

    def loadPath(self,path,format):
        load_files =  glob.glob(path+'/'+format)
        load_files.sort()
        for load_file in load_files:
            print("Processing file {0}".format(load_file))
            self.loadFile(load_file)
        self.batch_counter +=1
        print("Commiting batch {0}. Total Tweets ={1}".format(self.batch_counter,self.total_tweets))
        self.dbconn.commit()
    # @END LoadTwitterData

    # @BEGIN LoadTwitterDatafromFile @DESC Read and loads a single twitter file
    # @IN file   
    # @IN twitter_file 
    # @OUT tweet
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
    # @END LoadTwitterDatafromFile


    # @BEGIN LoadSingleTweet @DESC Reads, cleans and loads a single tweet in json format
    # @IN tweet 
    # @IN onlinetweet
    # @OUT Processedtweet  
    def loadTweet(self,tweet):
    # @END LoadSingleTweet
        # @BEGIN TwitterType @DESC Analyses tweet to determine if it is a retweet
        # @IN Processedtweet
        # @OUT Tweeted
        # @OUT ReTweeted
        if not self.isRetweeted(tweet):
        # @END TwitterType

        # @BEGIN ProcessTweet  @DESC Process only tweets
        # @IN Tweeted
        # @OUT JsonTweet
            try:
        # @END ProcessTweet 
                # @BEGIN ExtractTweetId @DESC Extracts twitter ID from Json Object
                # @IN JsonTweet
                # @OUT Id @AS TweetID
                id=tweet['id']
                # @END ExtractTweetId

                # @BEGIN ExtendedTweet @DESC Analyzes if it is a extented tweet
                # @IN JsonTweet
                # @OUT ExtendedTweet
                # @OUT RegularTweet
                # @OUT OriginalText
                if not self.isExtended(tweet):
                # @END ExtendedTweet
                    # @BEGIN RegularEntities @DESC Extracts data for regular tweet
                    # @IN RegularTweet
                    # @OUT RegularEntity
                    # @OUT RegularText
                    entities=self.getEntities(tweet)
                    text=self.getText(tweet)
                    # @END RegularEntities
                else:
                    # @BEGIN ExtendedEntities @DESC Extracts data for extended tweet
                    # @IN ExtendedTweet
                    # @OUT ExtendedEntity
                    # @OUT ExtendedText
                    entities=self.getExtendedEntities(tweet)
                    text=self.getExtendedText(tweet)
                    # @END ExtendedEntities
                # @BEGIN ExtractEntities @DESC EXtracts text and Entities for processing
                # @IN RegularEntity
                # @IN RegularText
                # @IN ExtendedEntity
                # @IN ExtendedText
                # @OUT Entity
                # @OUT Text
                # @END ExtractEntities

                # @BEGIN SaveOriginalText @DESC Saves Original Text for future reference
                # @IN OriginalText
                # @OUT SavedText
                origtext=text
                # @END SaveOriginalText

                # @BEGIN removeHashtags @DESC Removes Hastags from text
                # @IN Entity
                # @IN Text
                # @OUT RemovedHashtagsText
                text=self.removeHashtags(text,self.getEntitiesHashtags(entities))             
                # @END RemoveHashtags

                # @BEGIN removeUrls @DESC Removes Urls from text
                # @IN Entity
                # @IN Text
                # @OUT RemovedUrlsText              
                text=self.removeUrls(text,self.getEntitiesUrls(entities))            
                if self.hasUrl(text):
                    text=self.removeUrl(text)
                # @END removeUrls

                # @BEGIN removeUserMentions @DESC Removes User Mentions from text
                # @IN Entity
                # @IN Text
                # @OUT RemovedUserMentionsText
                text=self.removeUserMentions(text,self.getEntitiesUserMentions(entities))   
                # @END removeUserMentions

                # @BEGIN removeMultiline @DESC Eliminates end of line characters
                # @IN RemovedHashtagsText
                # @IN RemovedUrlsText
                # @IN RemovedUserMentionsText
                # @OUT removeMultilineText
                text=self.removeMultiline(text)
                # @END removeMultiline

                # @BEGIN makeLowerCase @DESC Converts text to lowercase
                # @IN removeMultilineText
                # @OUT makeLowerCaseText
                text=self.makeLowerCase(text)
                # @END makeLowerCase

                # @BEGIN removeNumbers @DESC Remove Numeric text
                # @IN makeLowerCaseText
                # @OUT removeNumbersText
                text=self.removeNumbers(text)
                # @END removeNumbers

                # @BEGIN expandContractions @DESC Expands Contractions
                # @IN removeNumbersText
                # @OUT expandContractionsText
                text=self.expandContractions(text)
                # @END expandContractions

                # @BEGIN removePosessives @DESC Eliminates possesives forms of nouns
                # @IN expandContractionsText
                # @OUT  removePosessivesText
                text=self.removePosessives(text)
                # @END removePosessives

                # @BEGIN removeUnicodeSymbols @DESC Eliminates Simbols in unicode from text
                # @IN removePosessivesText
                # @OUT removeUnicodeSymbolsText
                text=self.removeUnicodeSymbols(text)
                # @END removeUnicodeSymbols

                # @BEGIN removePunctuations @DESC Eliminates Punctuation Characters
                # @IN removeUnicodeSymbolsText
                # @OUT removePunctuationsText
                text=self.removePunctuations(text)
                # @END removePunctuations

                # @BEGIN removeBlanks @DESC deletes duplicate Spaces from Text 
                # @IN removePunctuationsText
                # @OUT removeBlanksText
                text=self.removeBlanks(text)
                # @END removeBlanks

                # @BEGIN tokenize @DESC Converts Text to tokens
                # @IN removeBlanksText
                # @OUT tokens
                tokens=self.tokenize(text)
                # @END tokenize

                # @BEGIN removeStopWords @DESC Removes Stop Words
                # @IN tokens
                # @OUT removeStopWordsTokens
                tokens=self.removeStopWords(tokens)
                # @END removeStopWords

                # @BEGIN lemmatize @DESC Applies Lematization to the text
                # @IN removeStopWordsTokens
                # @OUT lemmatizeTokens
                tokens=self.lemmatize(tokens)
                # @END lemmatize

                # @BEGIN removeShortWords @DESC  Eliminates words less than 3 characters
                # @IN lemmatizeTokens
                # @OUT removeShortWordsTokens
                tokens=self.removeShortWords(tokens)  
                # @END removeShortWords

                # @BEGIN CreateTextFromTokens @DESC Converts tokens back to text
                # @IN removeShortWordsTokens
                # @OUT CleanText
                text=' '.join(tokens)
                # @END CreateTextFromTokens 
                
                # @BEGIN StartTransaction @DESC Start database transaction to insert data
                # @IN CleanText
                # @OUT FinalText
                # @OUT DbConnection
                self.startTransaction
                # @END StartTransaction

                # @BEGIN insertTweet @DESC inserts data into Tweets table
                # @IN TweetID
                # @IN FinalText
                # @IN SavedText
                # @IN DbConnection
                # @OUT TweetsInserted    
                self.insertTweet(id,text,origtext)
                # @END insertTweet

                # @BEGIN insertHashtags @DESC Inserts data into Hashtags table
                # @IN TweetID
                # @IN Entity
                # @IN DbConnection
                # @OUT HashtagsInserted
                self.insertHashtags(id,self.getEntitiesHashtags(entities))
                # @END insertHashtags
                
                # @BEGIN insertUrls @DESC Insert data into Urls table.
                # @IN TweetID
                # @IN Entity
                # @IN DbConnection
                # @OUT UrlsInserted
                self.insertUrls(id,self.getEntitiesUrls(entities))
                # @END insertUrls
                
                # @BEGIN insertUserMentions @DESC Insert data into Usermentions table
                # @IN TweetID
                # @IN Entity
                # @IN DbConnection
                # @OUT UserMentionsInserted           
                self.insertUserMentions(id,self.getEntitiesUserMentions(entities))
                # @END  insertUserMentions

                # @BEGIN insertTokens @DESC Insert data into Tokens and Tokens_tweets tables
                # @IN TweetID
                # @IN removeShortWordsTokens
                # @IN DbConnection
                # @OUT TokensInserted
                self.insertTokens(id,tokens)
                # @END insertTokens

                # @BEGIN endTransaction @DESC Completes db transaction
                # @IN TokensInserted
                # @IN UserMentionsInserted
                # @IN UrlsInserted
                # @IN HashtagsInserted
                # @IN TweetsInserted
                # @OUT InsertedTweets
                self.endTransaction()
                # @END endTransaction

            except sqlite3.IntegrityError:
                print ("------------------------------------------------------------------------------------")
                pass
            except KeyError:
                print ("------------------------------------------------------------------------------------")
                pass
            except Exception as dberror:
                traceback.print_exc()
                print('Error inserting tweetid: {0}\nMessage: {1}'.format(id, str(dberror)))
                self.dbconn.rollback()
        # @BEGIN ProcesReTweet @DESC  Currently retweets are discarted
        # @IN ReTweeted
        # @OUT RejectedTweets
        else:
            pass
        # @END ProcesReTweet
        
    # @END TwitterDataCleaning

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
        self.total_tweets=result[0]
        cursor.execute(self.tokens_select_all)
        results=cursor.fetchall()
        for result in results:
            data=(math.log2(self.total_tweets/result[1]),result[0])
            cursor.execute(self.tokens_update_idf,data)
    
    def trimData(self):              
        cursor = self.dbconn.cursor()
        cursor.execute(self.snapshots_select_count_all)
        result=cursor.fetchone()
        snapshot_number=result[0]
        if snapshot_number > int(self.keep_batch):
            print("-----------------------------------------------------")
            print("Trimming database from {0} snaphots to {1}".format(snapshot_number,self.keep_batch))            
            cursor.execute(self.pragma_on)            
            data=[int(self.keep_batch)]
            cursor.execute(self.tweets_delete_older,data)      
            cursor.execute(self.sql_changes)
            result=cursor.fetchone()
            print("Number of tweets deleted {0}".format(result[0]))
            cursor.execute(self.snapshots_delete_older,data)
            cursor.execute(self.sql_changes)
            result=cursor.fetchone()
            print("Number of snpshots deleted {0}".format(result[0]))
            cursor.execute(self.tokens_tweets_delete)
            cursor.execute(self.sql_changes)
            result=cursor.fetchone()
            print("Number of tokens_tweets deleted {0}".format(result[0]))
            cursor.execute(self.update_tokens_doc_number)            
            cursor.execute(self.sql_changes)
            result=cursor.fetchone()
            print("Number of tokens updated {0}".format(result[0]))
            cursor.execute(self.tokens_delete_older)
            cursor.execute(self.sql_changes)
            result=cursor.fetchone()
            print("Number of tokens deleted {0}".format(result[0]))
            print("-----------------------------------------------------")
            self.updateIDF()
            self.dbconn.commit()
        else:
            print("No need to trim database snapshots {0}".format(snapshot_number))            

    def createsnapshot(self):
        cursor = self.dbconn.cursor()  
        data=[str(datetime.datetime.today())]
        cursor.execute(self.snapshots_insert,data)
        
    def startTransaction(self):
        self.dbconn.execute(self.pragma_on)

    def endTransaction(self):
        self.total_tweets +=1

        if self.total_tweets%self.batch_size == 0:
            self.batch_counter +=1
            self.createsnapshot()            
            self.dbconn.commit()
            self.trimData()
            self.dbconn.commit()
            self.updateIDF()        
            self.dbconn.commit()   
            
                    
            print("Commiting batch {0}. Total Tweets ={1}".format(self.batch_counter,self.total_tweets))
            
    