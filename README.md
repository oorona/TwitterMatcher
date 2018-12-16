# TwitterMatcher

TwitterMatcher application that allows do to syntagmatic analysis for term on twitter Feed. This application captures, cleans and stores tweets for a twitter feed to do further analysis. Once the data is available the main class provides all the logic to calculate mutual information and entropy for the tokens in the text. Syntagmatic relationships are found calculating the mutual information using a KL-divergence algorithm and using the IDF and TF to determine the tokens with the highest mutual information from the capture text.
The application can work in 2 modes. In the online mode all tweets are capture and process directly into the database. The application can save the tweet feed into files for further reference or future load to the database. A good loader tool is provided so that offline save files can be also load to the system.
Most of the settings are configured by editing or modifying configuration files under config folder.
The project was developed using Python 3 used of external libraries was reduce to minimal. The only library required is tweepy.  The project includes 4 samples applications that can used to have a sense of the capabilities of the packages. If the visualizer application is used, then matplolib will also be required for visualization.

## Syntagmatic Relationship finder

There are 3 main components to this application

### Data loader
First we must capture the twitter feed. This is done by TReader.py. This module uses clases under the streamer folder to either save data online or offline. The data loading process users 2 classes that extend the tweepy streamListener class called TwitterStreamer for offline operation or TwitterDbStreamer for online operation. They also defined a new classes called TwiiterCleaner that is in charge of doing all the database cleaning operation during capture of the tweet. Data cleaning operation are done only at the moment data is stored in database. That mean that during offline mode operation data cleaning operation will be done only during data load. On online mode operation all data is clean before is loaded.

All scripts to create database are located under `db/db.sql`. There is no need to create the database the application will create all necesary objects.

#### Insert Clean data to database.
Once all the data has been cleaned and breaking into components each piece must be inserted into the database.
This final step inserts all the data previously cleaned into a SQLite database

```Python
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
```

Once the data is loaded a sqlite is created with all the data properly cleaned and normalized. You can see a ER diagram of the database under the folder `db/dber.gif` file

#### Tables
The result of the script is a SQLite database what contains 6 different tables and their relationships.  There are 6 main tables/entities.  These tables together allow to execute all types of queries that can be used to run statistics operation over the number and frequency of terms on the tweets. Some of the data being extracted is probability of a token in collection, probability of join token in collection, IDF, Number of token in tweet, and number of times a token appears in the collection

|Table	|Description|
|-------|-----------|
|Tweets|Stores the clean data from the tweet as well as the original text for future reference.
|Urls|Stores all urls identified in tweet. Join Tweet table using tweet_id.
|Hashtags|Stores hashtags found in tweet. Join tweets table using tweet_id column.
|Usermentions|Stores user mentions found in tweet. Join tweets table using tweet_id column.
|Tokens|StoresIndividual tokens found in tweet, along with frequency and IDF.
|Tokens_Tweets|Links tweets and tokens tables and provides a frequency of tokens on the tweet.

#### Data Dictionary

##### Tweets

|Column Name|DataType|Description|
|-----------|--------|-----------|
Id|Integer|Integer matching the Tweet id from the API. Primary Key.
Message|Text|Clean Text after applying all data cleaning steps.
Original_message|Text|Text as original produced by the Twitter Feed without processing.
Capture_time|Date|Date with the capture time into the database.

##### Urls

|Column Name|DataType|Description|
|-----------|--------|-----------|
Tweet_id|Integer|Integer matching the Tweet id from the API. Foreign Key to tweets table.
Url|Text|Urls found in the text as provided by the full url. This is not the shortened version provided by twitter.

##### Hashtags

|Column Name|DataType|Description| 
|-----------|--------|-----------|
Tweet_id|Integer|Integer matching the Tweet id from the API. Foreign Key to tweets table.
Hashtag|Integer|Text containing the text of the hashtag that appeared in the tweet.

##### Usermentions

|Column Name|DataType|Description| 
|-----------|--------|-----------|
Tweet_id|Integer|Integer matching the Tweet id from the API. Foreign Key to tweets table.
User_id|Integer|Id of the twitter account as reported by the API.
name|Text|User’s name according with the twitter account.
Screen_name|Text|Account name in twitter.

##### Tokens

|Column Name|DataType|Description|
|-----------|--------|-----------|
Id|Text|Token id matching elements in the cleaned text. Primary Key.
Doc_number|Integer|Total number of documents where the token appears
Idf|Double|Inverse Document Frequency. Define as the log of doc_number/total_number of tweets from tweets table

##### Tokens_tweets

|Column Name|DataType|Description|
|-----------|--------|-----------|
Token_id|Text|Text matching token_id. Foreign Key to tokens table.
Tweet_id|Integer|Integer matching the Tweet id from the API. Foreign key to tweets table.
Token_number|Integer|Total Number of occurrences of the token in that particular tweet.


### Data Cleaning

The entire database cleaning process is conducted using python. There are multiple steps to clean the data, all of them are described below. All this steps are done by the StreamCleaner class.

#### Filtering and classifying tweets
Tweets must be identified to see if they are retweets or not. Retweets are eliminated during the process to avoid loading the same date multiple times to the database. If the tweet is extended tweet requires to access the data from a different data path.
Detecting if tweet is retweeted can be done if the retweeted_status is present.
```Python
def isRetweeted (self,tweet):
        if "retweeted_status" not in tweet:
            return False
        else:
            return True
```
Extended Tweets can be find using the extended tweet attribute.
```Python
def isExtended (self,tweet):
        if "extended_tweet" not in tweet:
            return False
        else:
            return True 
```
#### Extracting known entities
A Tweet can include entities such as urls, hashtags and user mentions. We must extract this piece of data so that we can use it for data cleaning and for inserting that data into the database.
This is done by looking at the entities object but must be done according with the tweet type.

```Python
def getEntities(self,tweet):
        return tweet['entities']

def getExtendedEntities(self,tweet):
        return tweet['extended_tweet']['entities']
```

#### Removing references to Urls
Any reference to urls must be removed from the text since they are being inserted and manage independently. 
Removing this piece can be done using extracting the url object and then using the indexes provided to remove the data.
```Python
def getEntitiesUrls(self,entity):
        return entity['urls']

def removeUrls(self,text,urls):
        for url in urls:
            starth=url['indices'][0]
            endh=url['indices'][1]
            blank = " "*(endh-starth)
            text=text[:starth]+blank+text[endh:]
        return text  
```

#### Removing references to other users
Any reference to urls must be removed from the text since they are being inserted and manage independently.
Removing this piece can be done using extracting the usermentions object and then using the indexes provided to remove the data.
```Python
def getEntitiesUserMentions(self,entity):
        return entity['user_mentions']

def removeUserMentions(self,text,usermentions):
        for usermention in usermentions:
            starth=usermention['indices'][0]
            endh=usermention['indices'][1]
            blank = " "*(endh-starth)
            text=text[:starth]+blank+text[endh:]
        return text    
```

#### Removing Hashtags
Any reference to urls must be removed from the text since they are being inserted and manage independently.
Removing this piece can be done using extracting the hashtags object and then using the indexes provided to remove the data.
```Python
def getEntitiesHashtags(self,entity):
        return entity['hashtags']
def removeHashtags(self,text,hashtags):
        for hashtag in hashtags:
            starth=hashtag['indices'][0]
            endh=hashtag['indices'][1]
            blank = " "*(endh-starth)
            text=text[:starth]+blank+text[endh:]
        return text
```

#### Eliminating end of line characters
Users and input their text in multiple lines. This is irrelevant for the data mining analysis.
This can be done by doing a search and replace of the end of line character.
```Python
def removeMultiline(self,text):
        return text.replace('\n',' ')
```

#### Making text to lower case
To keep consistency across all terms, text data is converted to lowercase to avoid duplication of terms and keep a consistent version.
This is just a simple operation to change the text to lowercase.
```Python
def makeLowerCase(self,text):
        return text.lower()
```

#### Removing numbers
At this point data mining techniques applied to this dataset do not benefit from numbers. This step could be reconsider in the future for other techniques.
This is completed by applying a regular expression for the class number where it appears 1 or more times.
```Python
def removeNumbers(self,text):
        return re.sub("\d+","",text)
 ```
 
#### Expanding languages contractions
In some languages like English tend to use contractions. Expanding these contractions allows us to keep a more concise corpus helps with analysis.
Expanding contractions requires a translation from a data dictionary located under cleaner/contration-lists folder. An object named ContractionExpander does the job.
```Python
def expandContractions(self, text):
        tokens=text.split()	
        con_tokens=[self.cont.expand(t) for t in tokens]
        return ' '.join(con_tokens)
```

#### Removing Possessives from nouns 
Eliminating the possessive form of nouns help us identify entities better.
This achieve using a regular expression looking for the ‘ symbol in both ascii and Unicode version.
```Python
def removePosessives(self,text):
        text= text.replace("'s"," ")
        return  text.replace("\u2019s"," ")
```

#### Eliminating Unicode symbols
User can add symbols to text. Some the symbols could add additional information for Sentiment Analysis but at this point they are being ignored.
Removing punctuations
Removing all punctuation allows us to focus only on the words.
This is done using a translation table.
```Python
transtable = str.maketrans('!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~',"")
def removePunctuations(self,text):
        return text.translate(self.transtable)
```
#### Removing extra blank spaces
Eliminating spaces allows to keep the text more compact and concise.
A regular expression is use to identify and remove multiple spaces.
```Python
 def removeBlanks(self,text):
        return re.sub(' +', ' ',text)
```
#### Doing tokenization
This step consists in breaking the text into individual tokens so that the data processing can continue as an individual token.
Once we reach this point the data is in a good format and creating individual tokes is achieve by splitting the text using spaces.
```Python
def tokenize(self,text):
        return text.split()
```
#### Removing stop words
Some words are so common in the language that eliminating them can helps us have a smaller dataset without losing too much information.
This process is achieve using a dictionary of stop words. The dictionary is located on uder the cleaner/stopwords-lists. A object called StopWorder is used to clean the data.
```Python
def removeStopWords(self,tokens):
        toks=[]
        for t in tokens:
            if not self.stop.isStopWord(t):
               toks.append(t)
        return toks
```

#### Lemmatization the tokens
Converting verbs to their root form helps us properly identify some of the relationship between entities.
This done using a lemmatization dictionary located under cleaner/lemmatization-lists. A special object call Lemmatizer is used to achieve this task.
```Python
def lemmatize(self,tokens):
        return [self.lemma.lemmatize(t) for t in tokens]
```

#### Removing short words
After removing stop words any word that is 2 characters or less then to be a mistake.  This is a step that can be reconsidered in the future.
```Python
def removeShortWords(self,tokens):
        toks=[]
        for t in tokens:
            if len(t)>2:
               toks.append(t)
        return toks
```

### Relationship Finder

Once the data has been cleaned and loaded all the sygntacmatic analysis calculations are completed by the Class RelFinder. This class provides multiple methods to calculate all the necesary values to implmente Mutual Information comparison using a KL divergence algorithm. This classes give you access to basic stats such as

#### Token count
Count of all the times a particular token apears in the db
```Python
def getTokenCount(self,token):
```
#### Token IDF
IDF calculation directly from database
```Python
def getTokenIDF(self,token):
```

#### Total Number of Tweets
Total number of tweets in datbase
```Python
def getTotalTweets(self):
```

#### Token Entropy
The entropy for a token smoothing is enable by default
```Python
def getTokenEntropy(self,token,smooth=True):
```

####  Token Probability
Probability of the token in that database
```Python
def getTokenProb(self,token):
```

#### Join Token Count
Number of times 2 tokens appear together
```Python
def getTokensJoinCount(self,token1,token2):    
```

#### Conditional Entropy
Conditional entropy for 2 given tokens, smoothin is enable by default
```Python
def getConditionalEntropy(self,token1,token2,smooth=True):    
```

#### Join Token Probability
Probaility of 2 token appearing together in the database.
```Python
def getJoinTokenProb(self,token1,token2):    
```

#### All tokens
Returns all token in the db
```Python
def getAllTokens(self):    
```

#### Context of Tokens
Returns all context of a token limited by a threshold value
```Python
def getContextTokens(self,token,threshold):    
```

#### Mutual Information
Returns the mutual information value for 2 given tokens. Smoothing is enabled by default
```Python
def getMutualInformation(self,token1,token2,smooth=True):
```

#### Top tokens
Returns the top tokens considering the IDF and TF. List is limited by a number of tokens to return
```Python
def getTopTokens(self,top_n_tokens):    
```

#### Top Mutual information List
Return a list of n tokens with higest mutual information for a given token. Limited by a threshold value
```Python
def getTopMutualInformation(self,word, top_n,threshold,smooth=True):
```
#### All Mutual Information
Return a list of top n tokens in the entire database with highest mutual information. Limited by threshold value and number of tokens
```Python
def getTopTokensMutualInformation(self,top_n_tokens,top_n_results,threshold,smooth=True):
```
#### Top condition Entropy
Return a list of top n token with lowest condition entropy for a given token.
```Python
def getTopConditionalEntropy(self,word, top_n,smooth=True):    
```

## Requirements 
You must have Python 3 and pip installed on your computer. 
Additionally, you will need 

[Tweepy](https://github.com/tweepy/tweepy)
if using the Visualizer application
[Matplotlib](https://github.com/matplotlib/matplotlib)

## Installation

1. Clone this repository
2. install
- pip install tweepy
- pip install matplolib

## Setup
1.	Defined the tweet capture mode by editing mode parameter under  `config/TReaderConfig.ini` file. You can leave the default of online mode 
2.	Set the term or terms you want to use to create your twitter feed by editing the Filter section under the `config/TReaderConfig.ini` file
3.	Set your twitter application credentials under the `config/TwitterCred.ini` file
4.	If you decided to your offline mode and store files on a folder you may need to edit the `config/StreamerClearnerConfig.ini` file.

## Data Capture
1.To work on online mode, make sure that the property mode is set to online. See setup above.
Execute
```
python TReader.py 
```
While this capture stream is running you can run all the analysis provided by the tool.
To close the capture stream just do ctrl+c on the capture window

2.To work on offline mode, make sure that the property mode is set to offline. See setup above.
Execute 
```
python TReader.py 
```
Since files will be save to the data folder. You will have to load tem to the database once the capture stream is complete. 
Once all the desire files have been captured, you can close the capture stream just do ctrl+c on the capture window.

In order to load the files to the database 
Execute
```
python LoadOfflineData.py -h
usage: LoadOfflineData.py [-h] path format batch_size keep_batch

Program to load offline Tweets files to database

positional arguments:
  path        Location of tweets file
  format      File name formats
  batch_size  Batch size number for commit records
  keep_batch  number of batches to store

optional arguments:
  -h, --help  show this help message and exit
```
## Usage

To see the application working is better to use the online mode.

1.While data capture mode is running 
2.Open second window.
3.Execute any of the following 4 applications
### List top words associated with a particular word
```
$ python TRelationsToken.py -h
usage: TRelationsToken.py [-h] [-t THRESHOLD] [-s SLEEP] [-nt LIMIT]
                          [-l LOOPS]
                          token

Program to list top relationships with a token

positional arguments:
  token                 Token for similary estimation

optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLD, --threshold THRESHOLD
                        Number of tokens to consider during IDF filtering
  -s SLEEP, --sleep SLEEP
                        Number of seconds to sleep before doing next analysis
  -nt LIMIT, --limit LIMIT
                        Top number of tokens to display
  -l LOOPS, --loops LOOPS
                        Number loops to do analysis

```
### List top relationships on entire database
```
python TRelationsAll.py -h
usage: TRelationsAll.py [-h] [-t THRESHOLD] [-s SLEEP] [-nt LIMIT]
                        [-tl TOKENLIMIT] [-l LOOPS]

Program to visualize all top relationships

optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLD, --threshold THRESHOLD
                        Number of tokens to consider during IDF filtering
  -s SLEEP, --sleep SLEEP
                        Number of seconds to sleep before doing next analysis
  -nt LIMIT, --limit LIMIT
                        Top number of tokens to display
  -tl TOKENLIMIT, --tokenlimit TOKENLIMIT
                        Number of top tokens to do analysis
  -l LOOPS, --loops LOOPS
                        Number loops to do analysis
```
### Visualizer to show you the top words associated with a word

```
python VisualizerToken.py -h
usage: VisualizerToken.py [-h] [-t THRESHOLD] [-s SLEEP] [-l LIMIT] token

Program to visualize top relationships with a token

positional arguments:
  token                 Token for similary estimation

optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLD, --threshold THRESHOLD
                        Number of tokens to consider during IDF filtering
  -s SLEEP, --sleep SLEEP
                        Number of seconds to sleep before doing next analysis
  -l LIMIT, --limit LIMIT
                        Top number of tokens to display
```
### Visualizer to show all top relationships in the database.
```
python VisualizerAll.py -h
usage: VisualizerAll.py [-h] [-t THRESHOLD] [-s SLEEP] [-l LIMIT]
                        [-tl TOKENLIMIT]

Program to visualize all top relationships

optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLD, --threshold THRESHOLD
                        Number of tokens to consider during IDF filtering
  -s SLEEP, --sleep SLEEP
                        Number of seconds to sleep before doing next analysis
  -l LIMIT, --limit LIMIT
                        Top number of tokens to display
  -tl TOKENLIMIT, --tokenlimit TOKENLIMIT
                        Number of top tokens to do analysis
```
