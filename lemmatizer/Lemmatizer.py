import configparser

class Lemmatizer:

    worddict = {}
    listlang=[]
    
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("./config/TReaderConfig.ini")
        for key in config['Languages']: 
            self.listlang.append(config['Languages'][key])
            lemmafile ='./lemmatizer/lemmatization-lists/lemmatization-'+config['Languages'][key]+'.txt'
            with open(lemmafile, 'rb') as lineword:
                wordlist = lineword.read().decode('utf8').replace(u'\r', u'').split(u'\n')
                wordlist = [word.split(u'\t') for word in wordlist]
                
        for words in wordlist:
            if len(words) >1:
                self.worddict[words[1]] = words[0]    
    
    def lemmatize(self,word):
        return self.worddict.get(word,word)

