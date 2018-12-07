import configparser

class StopWorder:

    wordlist = []
    listlang=[]
    
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("./config/TReaderConfig.ini")
        for key in config['Languages']: 
            self.listlang.append(config['Languages'][key])
            stopfile ='./lemmatizer/stopword-lists/stopword-'+config['Languages'][key]+'.txt'
            with open(stopfile, 'rb') as lineword:
                self.wordlist = lineword.read().decode('utf8').replace(u'\r', u'').split(u'\n')
                
    
    def isStopWord(self,word):
        if word in self.wordlist:
            return True
        else:
            return False
    