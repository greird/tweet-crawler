# Tweet Crawler 🦎

This is a simple Twitter crawler that will fetch every tweets from the past week on a given topic (or more depending on your access to the Twitter API). 

The last tweet id is stored in the config file so that if you launch the same query again, it will start crawling tweets from the last retrieved and add them to the same csv file.

Tweets are stored in a csv file.

### Configuration

The crawler depends on the `twitter` package. 
```
pip install twitter
```

Create a `config.cfg` file next to `tweet_crawler.py` and fill it with the following code.
```
[twitter-api]
CONSUMER_KEY=
CONSUMER_SECRET=
ACCESS_TOKEN_KEY=
ACCESS_TOKEN_SECRET=
```

Complete the file with your very own Twitter API Keys and Tokens.

### Usage

`python tweet_crawler.py` in your terminal to launch the crawler and follow the instructions. 

If manually interrupted, it will automatically save tweets to a csv before shutting down.