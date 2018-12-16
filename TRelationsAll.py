from RelFinder import RelFinder
from streamer.StreamCleaner import StreamCleaner
import time
import sys, signal
import argparse



def signal_handler(signal, frame):
    print("\nEnding Analysis")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    
    relf = RelFinder()
    rownum="{:<5}{:<20}{:<20}{:<15}{:<10}"
    previous_results=()
    i=0

    parser = argparse.ArgumentParser(description='Program to load offline Tweets files to database')        
    parser.add_argument('-t','--threshold',default=100,type=int,help='Number of tokens to consider during IDF filtering')
    parser.add_argument('-s','--sleep', default=5,type=int,help='Number of seconds to sleep before doing next analysis')
    parser.add_argument('-nt','--limit',default=10,type=int, help='Top number of tokens to display')
    parser.add_argument('-tl','--tokenlimit',default=50,type=int, help='Number of top tokens to do analysis')
    parser.add_argument('-l','--loops',default=5,type=int, help='Number loops to do analysis')

    args = vars(parser.parse_args())
    threshold = args ['threshold']
    sleep = args['sleep']
    limit=args['limit']
    tokenlimit=args['tokenlimit']
    loops=args['loops']

    try:
        while i < loops :
            results=relf.getTopTokensMutualInformation(tokenlimit,limit,threshold,True)
            if len (results) >0:
                if i==0:
                    previous_results=results.copy()
                
                for j in range(limit):
                    if results[j][1]==previous_results[j][1]:
                        change="No change"
                    else:
                        found=False
                        for k in range(limit):
                            if results[j][1]==previous_results[k][1]:
                                change="{:+} before {} now {}".format(previous_results[k][3]-results[j][3],previous_results[k][3]+1,results[j][3]+1)
                                found=True
                        if not found:                            
                            change="New Token"
                    print (rownum.format(results[j][3]+1,results[j][0],results[j][1],round(results[j][2],7),change))
                print("-"*80)
                previous_results=results.copy()                   
                time.sleep(sleep)
                i+=1
            else:
                print("No data found for that token")
                exit (0)
    except KeyboardInterrupt:
        print('\nProgram ended!')
