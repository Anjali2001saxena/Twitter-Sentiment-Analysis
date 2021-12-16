import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from flask import Flask, render_template, request
app = Flask(__name__)

class TwitterClient(object):
    def __init__(self):
        consumer_key = 'qEdFAFBwmfSgpHy7oBArOvMIE'
        consumer_secret = 'hdGZ7LhQJHgvIFrjB7z9AaThtmX1vruR6IjcLcrOoTR5zlcE2i'
        access_token = '1293052539802271745-XPGtnbr1Jj5dObmzjjuOOh1Aj4OeKc'
        access_token_secret = 'jPEgLpeR9UDHk9tepXnBURmcgMqIYyzPNfS36u8ssqTeG'
        
        try:
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(self.auth) 
        except:
            print("Error : Authentication Failed")
            
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def get_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
        
    def get_tweets(self, query, count):
        tweets = []
        
        try:
            fetched_tweets = self.api.search(q = query, count = count)
            
            for tweet in fetched_tweets:
                parsed_tweet = {}
                parsed_tweet['text'] = tweet.text
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
                    
            return tweets
        
        except tweepy.TweepError as e:
            print("Error : " + str(e))
            
    def get_info(self, id, count):
        tweets = []
        
        try:
            fetched_tweets = self.api.user_timeline(id, count=count)
            user = self.api.get_user(id)
            name = user.screen_name
            
            for tweet in fetched_tweets:
                parsed_tweet = {}
                parsed_tweet['text'] = tweet.text
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
                    
            info = {"name": name, "tweets": tweets}
            return info
        
        except tweepy.TweepError as e:
            print("Error : " + str(e))
            
def main1(query):
    api = TwitterClient()
    tweets = api.get_tweets(query , count=200)
        
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    p = len(ptweets)
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    n = len(ntweets)
    print("Neutral tweets percentage: {} % ".format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets)))
    nu = len(tweets) -(len( ntweets )+len( ptweets))
    ans = [p, n, nu ]
    return ans

def main2(id):
    api = TwitterClient()
    info = api.get_info(id, count=200) 
    name = info["name"]
    tweets = info["tweets"]
    
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    p = len(ptweets)
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    n = len(ntweets)
    print("Neutral tweets percentage: {} % ".format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets)))
    nu = len(tweets) -(len( ntweets )+len( ptweets))
    ans = [p, n, nu, name]
    return ans

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/user')
def user():
    return render_template('user_search.html')

@app.route('/user/submit', methods=['POST', 'GET'])
def user_analysis():
    if request.method == 'POST':
        id = request.form['user_id']
        if(id):
            answer = main2(id);
            pos = answer[0]
            neg = answer[1]
            neu = answer[2]
            user = answer[3]
            return render_template("user_dashboard.html", positive = pos, negative= neg, neutral = neu, name = user)

@app.route('/hashtag')
def hashtag():
    return render_template('topic_search.html')

@app.route('/hashtag/submit', methods=['POST', 'GET'])
def topic_analysis():
    if request.method == 'POST':
        topic = request.form['topic']
        if(topic):
            answer = main1(topic);
            pos = answer[0]
            neg = answer[1]
            neu = answer[2]
            return render_template("hashtag_dashboard.html", positive = pos, negative= neg, neutral = neu, topic=topic)
        
if __name__ == '__main__':
    app.run()