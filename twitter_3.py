# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 21:25:34 2023

@author: Rafa_
"""
#pip3 install --user --upgrade -e git+https://github.com/twintproject/twint.git@origin/master#egg=twint

import twint
from textblob import TextBlob
import folium
import pandas as pd
import nest_asyncio
import datetime
import csv

#define date today
now = datetime.datetime.now()

today = (now - datetime.timedelta(hours = 3))
today = now.strftime('%Y-%m-%d %H:%M:%S')
print(today)

day = datetime.datetime.now().day
month = datetime.datetime.now().month
year = datetime.datetime.now().year

# Define a list of locations to collect Twitter data for
url = 'loc_ce_centroide.csv'
data = pd.read_csv(url,sep =',')
print(data.head(5))

data = data.rename(columns={'mun_nome': 'name'})
locations= data.to_dict('records')

print((locations) )

# Configure Twint search parameters
config = twint.Config()
config.Hide_output = True
config.Limit = 1000
config.Store_object = True
config.Lang = 'pt'
config.Since = f'{year}-{month}-{day}' #today
#config.Until = '2023-02-15'
#config.Popular_tweets = True
config.Near = ''
config.Geo = ''
#config.Location = True
config.Count = True
config.Pandas = True
def get_sentiments(score):
    
    if score > 0.6:
        return 'positive'
    elif score < 0.4:
        return 'negative'
    else:
        return 'neutral'
    
def get_sentiment_score(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Collect Twitter data for each location
data = []

map = folium.Map(location=[-5.1580336,-41.354628], zoom_start=5)

for location in locations:
    
    #for i in range(0, 183):
    config.Search = f'chuva geocode:{location["lat"]},{location["lon"]},20km'
    #config.Search = f'calor geocode:{location["lat"]},{location["lon"]},20km'
    config.Near = location
    config.Geo = f'{location["lat"]},{location["lon"]},10km'
    twint.run.Search(config)
    tweets = twint.output.tweets_list
	
    for tweet in tweets:
        sentiment_score = get_sentiment_score(tweet.tweet)
        df = twint.storage.panda.Tweets_df
        print(tweet.tweet)
        sentiment_scores = [get_sentiment_score(tweet.tweet) for tweet in tweets]
        sentiment_score = sum(sentiment_scores) / len(sentiment_scores) if len(sentiment_scores) > 0 else 0
        data.append({'name': location['name'], 'lat': location['lat'], 'lon': location['lon'],
                'tweets': tweets, 'sentiment_score': sentiment_score})
        twint.output.tweets_list = []

# Create a map with markers for each location

for location in data:
    tweets_html = ''.join(f'<li>{tweet.tweet}</li>' for tweet in location['tweets'])
    popup_text = f"{location['name']}\nTweets:<ul>{tweets_html}</ul>\n Date:{df['date'][0]}\nSentiment Score: {location['sentiment_score']}"
    folium.CircleMarker(location=[location['lat'], location['lon']], radius = 5, fill_color='blue', color = 'blue', popup=popup_text).add_to(map)

map.save('map_twtter_all.html')

