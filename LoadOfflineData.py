from streamer.StreamCleaner import StreamCleaner
import argparse

def main():
    parser = argparse.ArgumentParser(description='Program to load offline Tweets files to database')        
    parser.add_argument('path', help='Location of tweets file')
    parser.add_argument('format', help='File name formats')
    parser.add_argument('batch_size',help='Batch size number for commit records')
    parser.add_argument('keep_batch',help='number of batches to store')
    args = vars(parser.parse_args())
    path = args ['path']
    format = args ['format']
    batch_size = args['batch_size']
    keep_batch=args['keep_batch']
    loader =StreamCleaner(int(batch_size),int(keep_batch))
    loader.loadPath(path,format)

if __name__ == "__main__":
    main()
