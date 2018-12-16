# TwitterMatcher

TwitterMatcher application that allows do to syntagmatic analysis for term on twitter Feed. This application captures, cleans and stores tweets for a twitter feed to do further analysis. Once the data is available the main class provides all the logic to calculate mutual information and entropy for the tokens in the text. Syntagmatic relationships are found calculating the mutual information using a KL-divergence algorithm and using the IDF and TF to determine the tokens with the highest mutual information from the capture text.
The application can work in 2 modes. In the online mode all tweets are capture and process directly into the database. The application can save the tweet feed into files for further reference or future load to the database. A good loader tool is provided so that offline save files can be also load to the system.
Most of the settings are configured by editing or modifying configuration files under config folder.
The project was developed using Python 3 used of external libraries was reduce to minimal. The only library required is tweepy.  The project includes 4 samples applications that can used to have a sense of the capabilities of the packages. If the visualizer application is used, then matplolib will also be required for visualization.

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
1.	Defined the tweet capture mode by editing mode parameter under  ./config/TReaderConfig.ini file. You can leave the default of online mode 
2.	Set the term or terms you want to use to create your twitter feed by editing the Filter section under the ./config/TReaderConfig.ini file
3.	Set your twitter application credentials under the TwitterCred.ini file
4.	If you decided to your offline mode and store files on a folder you may need to edit the ./config/StreamerClearnerConfig.ini file.

## Functionality
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
