import tweepy
from datetime import datetime
from pymongo import MongoClient
import streamlit as st

# Twitter API credentials
consumer_key = "fC9BbMGzfMNTNljch4PqR6Ynv"
consumer_secret = "1nnl3JfwPMh9sqS3ppaDnI6srpEX2rlbQHWjckDgLD84ajZ2b8"
access_token = "1666368124332154887-gIvFvmscz2as2BqF7giJMsDifKmE6W"
access_token_secret = "jd3Q4SAAc92I2JlOqQ0EP80IYvTRYJKqmIXqCerrjy5TO"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["twitter"]
collection = db["tweets"]

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def scrape_twitter_data(keyword, start_date, end_date, tweet_count):
    tweets = tweepy.Cursor(api.search_tweets,
                           q=keyword,
                           lang="en",
                           result_type="recent",
                           tweet_mode="extended",
                           since=start_date,
                           until=end_date).items(tweet_count)

    scraped_data = []
    for tweet in tweets:
        data = {
            "date": tweet.created_at,
            "tweet": tweet.full_text,
            "user": tweet.user.screen_name,
            "retweet_count": tweet.retweet_count,
            "favorite_count": tweet.favorite_count,
            "source": tweet.source
        }
        scraped_data.append(data)

    return scraped_data

def main():
    st.title("Twitter Data Scraper")
    keyword = st.text_input("Enter the keyword or hashtag to search:")
    start_date = st.date_input("Select the start date:")
    end_date = st.date_input("Select the end date:")
    tweet_count = st.number_input("Enter the number of tweets to scrape:", min_value=1, value=100)

    if st.button("Scrape"):
        st.info("Scraping data...")
        tweet_data = scrape_twitter_data(keyword, start_date, end_date, tweet_count)

        # Insert the scraped data into MongoDB
        for data in tweet_data:
            document = {
                "date": data["date"],
                "tweet": data["tweet"],
                "user": data["user"],
                "retweet_count": data["retweet_count"],
                "favorite_count": data["favorite_count"],
                "source": data["source"],
                "number_of_tweets": len(tweet_data)
            }
            collection.insert_one(document)

        st.success("Data scraped and inserted into MongoDB.")

if __name__ == "__main__":
    main()