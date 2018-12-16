import matplotlib.pyplot as plt
import matplotlib.lines as lines
from matplotlib.animation import FuncAnimation
import matplotlib.cm as cm
import itertools
from graph.RankLine import RankLine
from RelFinder import RelFinder
import argparse


tt=()
tokens =[]
new_tokens=[]
firstpop=True

colors=[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
framewidth=100
scrollpoint=80
xlabel='Loops'
Ylabel='Rankings'
relf = RelFinder()

parser = argparse.ArgumentParser(description='Program to visualize all top relationships')        
parser.add_argument('-t','--threshold',default=100,type=int,help='Number of tokens to consider during IDF filtering')
parser.add_argument('-s','--sleep', default=1,type=int,help='Number of seconds to sleep before doing next analysis')
parser.add_argument('-l','--limit',default=10,type=int, help='Top number of tokens to display')
parser.add_argument('-tl','--tokenlimit',default=50,type=int, help='Number of top tokens to do analysis')

args = vars(parser.parse_args())
threshold = args ['threshold']
sleep = args['sleep']
limit=args['limit']
tokenlimit=args['tokenlimit']

fig =plt.figure("All Tokens")
yticks=[i for i in range(limit)]
colors=[i/limit for i in range(limit)]
ax = plt.axes(xlim=(0, framewidth),ylim=(limit +1 ,0))
ax.set_frame_on(True)
plt.xlabel(xlabel)
plt.ylabel(Ylabel)
plt.title("Top Syntagmatic Relationships ")
plt.grid(True)

colors = iter(cm.rainbow(colors))

results=relf.getTopTokensMutualInformation(tokenlimit,limit,threshold,True)

for res in results:
    line = RankLine([0], [limit-res[3]], label=res[0]+"-"+res[1],color=next(colors),lw=3)
    line = ax.add_line(line)
    tokens.append([res[0]+"-"+res[1],line,[0],[res[3]+1]])


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
    global firstpop

    results=relf.getTopTokensMutualInformation(tokenlimit,limit,threshold,True)
    tokenstoupdate= []

    for token in tokens:
        found=False
        if frame >scrollpoint:
            token[1].axes.set_xlim(frame-scrollpoint,frame-scrollpoint+framewidth)
            token[2].pop(0)
            token[3].pop(0)
            if firstpop :
                token[2].pop(0)
                token[3].pop(0)
                token[2].pop(0)
                token[3].pop(0)
            token[1].set_data(token[2],token[3]) 
        for res in results:
            if token[0] == res[0]+"-"+res[1]:  
                token[2].append(frame)
                token[3].append(res[3]+1)      
                token[1].set_data(token[2],token[3])                
                found=True
        if not found:
            tokenstoupdate.append(token[0])
    i=0
    if frame >scrollpoint:
        firstpop=False

    for res in results:
        found=False
        for token in tokens:
            if res[0]+"-"+res[1] == token [0]:
                found=True
        if not found:
            for token in tokens:
                if token[0]==tokenstoupdate[i]:
                    token[0]=res[0]+"-"+res[1]
                    
                    for  j in range(len(token[3])-1):
                        token[3][j]=None
                    token[2].append(frame)
                    token[3].append(res[3]+1)    
                    token[1].set_data(token[2],token[3])                
                    token[1].text.set_text(res[0]+"-"+res[1])   
            i+=1
    
    for token in tokens:
        l=token[1]
        tt=tt+(l,)
    return tt 

ani = FuncAnimation(fig, update,interval=sleep*1000, blit=False)
plt.show()