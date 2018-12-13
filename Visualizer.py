import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.cm as cm
import itertools
from graph.RankLine import RankLine
from RelFinder import RelFinder
import argparse


tt=()
#t=()
tokens =[]
new_tokens=[]
yticks=[1,2,3,4,5,6,7,8,9,10]
colors=[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
i=0
relf = RelFinder()
scrollpoint=80

parser = argparse.ArgumentParser(description='Program to load offline Tweets files to database')        
parser.add_argument('token', help='Token for similary estimation')
parser.add_argument('-t','--threshold',default=100,type=int,help='Number of tokens to consider during IDF filtering')
parser.add_argument('-s','--sleep', default=5,type=int,help='Number of seconds to sleep before doing next analysis')
parser.add_argument('-l','--limit',default=10,type=int, help='Top number of tokens to display')
args = vars(parser.parse_args())
word = args ['token']
threshold = args ['threshold']
sleep = args['sleep']
limit=args['limit']


results=relf.getTopMutualInformation(word,limit,threshold,True)

fig =plt.figure()
ax = plt.axes(xlim=(0, 100),ylim=(11,0))
colors = iter(cm.rainbow(colors))

for res in results:
    some = RankLine([0], [10-res[3]], animated=True, label=res[1],color=next(colors),lw=3)
    i+=1   
    ax.add_line(some)
    tokens.append([res[1],some,[0],[res[3]+1]])
plt.yticks(yticks)

def init():
    tt=()
    global tokens
    
    for token in tokens:
        l=token[1]
        tt=tt+(l,)

    return tt 

def update(frame):
    tt= ()
    global tokens
    global ax
    results=relf.getTopMutualInformation(word,limit,threshold,True)
    tokenstoupdate= []


    for token in tokens:
        found=False
        if frame >scrollpoint:
                token[1].axes.set_xlim(frame-scrollpoint,frame-scrollpoint+100)
                token[2]=token[2][:scrollpoint]
                token[3]=token[3][:scrollpoint]
                print(len(token[2]))
                print(len(token[3]))
                token[1].set_data(token[2],token[3]) 
        for res in results:
            if token[0] == res [1]:  
                token[2].append(frame)
                token[3].append(res[3]+1)                
                token[1].set_data(token[2],token[3])                
                found=True
        if not found:
            print('token {} not found in results'.format(token[0]))                            
            tokenstoupdate.append(token[0])
    print ("Total missing items {}".format(len(tokenstoupdate)))
    i=0
    for res in results:
        found=False
        for token in tokens:
            if res[1] == token [0]:
                found=True
        if not found:
            print('token {} not found in list'.format(res[1]))                            
            for token in tokens:
                if token[0]==tokenstoupdate[i]:
                    print ("Replacing {0} with {1}".format(token[0],res[1]))   
                    token[0]=res[1]
                    
                    for  j in range(len(token[3])-1):
                        token[3][j]=None
                    if frame+1 != len(token[3]):
                        print ("*********frame={} token len={}".format(frame+1,len(token[3])))
                    token[2].append(frame)
                    token[3].append(res[3]+1)    
                    token[1].set_data(token[2],token[3])                
                    token[1].text.set_text(res[1])   
            i+=1
 

    for token in tokens:
        #print(len(token[2]))
        #print(len(token[3]))
        l=token[1]
        tt=tt+(l,)
    #if total!=55:
    #    print ("**************Not 55 {}".format(total))

    return tt 

ani = FuncAnimation(fig, update,interval=sleep*1000,init_func=init, blit=True)
plt.show()