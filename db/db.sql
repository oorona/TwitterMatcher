drop index tt_token_id;
drop index tt_tweet_id;
drop table tokens_tweets;
drop table tokens;
drop table usermentions;
drop table hashtags;
drop table urls;
drop table tweets;
drop table snapshots;


create table tweets (id INTEGER PRIMARY KEY,
       message TEXT not null,
       original_message text not null,
       capture_time TEXT not null); 
create table urls(tweet_id INTEGER not null,
       url TEXT not null,
       FOREIGN KEY(tweet_id) REFERENCES tweets(id) ON DELETE CASCADE);
create table hashtags(tweet_id INTEGER not null,
       hashtag TEXT not null,
       FOREIGN KEY(tweet_id) REFERENCES tweets(id) ON DELETE CASCADE); 
create table usermentions(tweet_id INTEGER not null,
       user_id TEXT not null,
       name TEXT not null,
       screen_name TEXT not null,
       FOREIGN KEY(tweet_id) REFERENCES tweets(id) ON DELETE CASCADE); 
create table tokens(id text not null primary key,
       doc_number INTEGER not null,
       idf FLOAT not null );  
create table tokens_tweets (token_id text not null,
       tweet_id INTEGER not null,
       token_number integer not null,
       FOREIGN KEY(tweet_id) REFERENCES tweets(id) ON DELETE CASCADE,
       FOREIGN KEY(token_id) REFERENCES tokens(id)); 
create table snapshots (id INTEGER PRIMARY KEY,
        capture_time TEXT);
create index tt_token_id 
        ON tokens_tweets(token_id); 
create index tt_tweet_id 
        ON tokens_tweets(tweet_id);         
create index t_capture 
        ON tweets (capture_time);