
import sqlite3
import configparser
import math

class RelFinder:
    files_loaded=0
    total_tweets=0
    tweet_number=0
    
    config = configparser.ConfigParser()
    config.read("./config/DbSettings.ini")
    db_file =config['Database']['db_file_name']
    dbconn = sqlite3.connect(db_file)

    
    tokens_select_token_count =config['Sql']['tokens_select_token_count']
    tokens_select_idf =config['Sql']['tokens_select_idf']
    tweets_select_total =config['Sql']['tweets_select_total']
    tokens_tweets_tokens_join=config['Sql']['tokens_tweets_tokens_join']
    tokens_select_all=config['Sql']['tokens_select_all']

    def getTokenCount(self,token):
        cursor = self.dbconn.cursor()
        data=[token]            
        cursor.execute(self.tokens_select_token_count,data)
        return cursor.fetchone()[0]

    def getTokenIDF(self,token):
        cursor = self.dbconn.cursor()
        data=[token]            
        cursor.execute(self.tokens_select_idf,data)
        return cursor.fetchone()[0]

    def getTokensJoinCount(self,token1,token2):
        cursor = self.dbconn.cursor()
        data=(token1,token2)            
        cursor.execute(self.tokens_tweets_tokens_join,data)
        return cursor.fetchone()[0]

    def getTotalTweets(self):
        cursor = self.dbconn.cursor()
        cursor.execute(self.tweets_select_total)
        return cursor.fetchone()[0]

    def getTokenProb(self,token):
        self.total_tweets=self.getTotalTweets()
        return self.getTokenCount(token)/self.total_tweets

    def getTokenEntropy(self,token,smooth=True):
        if smooth:
            pe1=self.getTokenSmoothProb(token)
        else:
            pe1=self.getTokenProb(token)
        
        pe0=1-pe1
        
        if pe0 ==0 :
            p1=0
        else:
            p1=-1*pe0*math.log2(pe0)
        
        if pe1 ==0 :
            p2=0
        else:
            p2=-1*pe1*math.log2(pe1)
        
        return p1+p2
    
    def getConditionalEntropy(self,token1,token2,smooth=True):
        if smooth :
            p1e1=self.getTokenSmoothProb(token1)
            p2e1=self.getTokenSmoothProb(token2)
            pje11=self.getJoinTokenSmoothProb(token1,token2)            
        else:
            p1e1=self.getTokenProb(token1)
            p2e1=self.getTokenProb(token2)
            pje11=self.getJoinTokenProb(token1,token2)
        
        p1e0=1-p1e1
        pje10=p1e1-pje11
        pje01=p2e1-pje11
        pje00=1-pje11-pje10-pje01

        if pje00==0:
            m00=0
        else:
            m00=p1e0*(-1*pje00*math.log2(pje00))
        
        if pje10==0:
            m10=0
        else:
            m10=p1e0*(-1*pje10*math.log2(pje10))
        
        if pje01==0:
            m01=0
        else:
            m01=p1e1*(-1*pje01*math.log2(pje01))
        
        if pje11==0:
            m11=0
        else:
            m11=p1e1*(-1*pje11*math.log2(pje11))
        
        return m00+m10+m01+m11


    def getJoinTokenProb(self,token1,token2):
        self.total_tweets=self.getTotalTweets()
        return self.getTokensJoinCount(token1,token2)/self.total_tweets

    def getTokenSmoothProb(self,token):
        self.total_tweets=self.getTotalTweets()
        return (self.getTokenCount(token)+0.5)/(self.total_tweets+1)

    def getJoinTokenSmoothProb(self,token1,token2):
        self.total_tweets=self.getTotalTweets()
        return (self.getTokensJoinCount(token1,token2)+0.25)/(self.total_tweets+1)

    def getAllTokens(self):
        cursor = self.dbconn.cursor()
        cursor.execute(self.tokens_select_all)
        return cursor.fetchall()

    def getMutualInformation(self,token1,token2,smooth=True):
        
        if smooth :
            p1e1=self.getTokenSmoothProb(token1)
            p2e1=self.getTokenSmoothProb(token2)
            pje11=self.getJoinTokenSmoothProb(token1,token2)            
        else:
            p1e1=self.getTokenProb(token1)
            p2e1=self.getTokenProb(token2)
            pje11=self.getJoinTokenProb(token1,token2)
        

        p1e0=1-p1e1
        p2e0=1-p2e1
        pje10=p1e1-pje11
        pje01=p2e1-pje11
        pje00=1-pje11-pje10-pje01

        if p1e0==0 or p2e0==0 or pje00==0 :
            m00=0
        else:
            m00=pje00*math.log2(pje00/(p1e0*p2e0))
        
        if p1e1==0 or p2e0==0 or pje10==0:
            m10=0
        else:
            m10=pje10*math.log2(pje10/(p1e1*p2e0))
        
        if p1e0==0 or p2e1==0 or pje01==0:
            m01=0
        else:
            m01=pje01*math.log2(pje01/(p1e0*p2e1))
        
        if p1e1==0 or p2e1==0 or pje11==0:
            m11=0
        else:
            m11=pje11*math.log2(pje11/(p1e1*p2e1))
        
        return m00+m10+m01+m11

    def getAllMutualInformation(self,word, top_n,smooth=True):
        results= []
        for token in self.getAllTokens():
            if not token[0]==word:
                mi=self.getMutualInformation(word,token[0],smooth)                
                results.append((word,token[0],mi))
        
        results.sort(key =lambda x:x[2],reverse=True)
        
        for i in range(top_n):
            print (results[i])

    def getAllConditionalEntropy(self,word, top_n,smooth=True):
        results= []
        for token in self.getAllTokens():
            if not token[0]==word:
                mi=self.getConditionalEntropy(word,token[0],smooth)                
                results.append((word,token[0],mi))
        
        results.sort(key =lambda x:x[2],reverse=False)
        
        for i in range(top_n):
            print (results[i])

