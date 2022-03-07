# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from requests import get
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import random
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import datetime as dt
import csv 
import psycopg2
import time
from sklearn.feature_extraction.text import TfidfVectorizer

from helper_funcs.urls_to_soup_objects import *
from helper_funcs.clean_three_or_more_prices import *
from helper_funcs.clean_two_prices import *
from helper_funcs.soup_objects_to_df import *
from helper_funcs.dropping_funcs import *

# %%
# Create a Session and Retry object to manage the quota Craigslist imposes on HTTP get requests within a certain time period 
session = requests.Session()
retry = Retry(connect=5, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# %% [markdown]
# # Extracting Craigslist Data
# ## Get all state/region names

# %%
# Parse URL that contains all regions of Craigslist
all_sites_response = session.get('https://craigslist.org/about/sites')
all_sites_soup = BeautifulSoup(all_sites_response.text, 'html.parser')

# Extract part of webpage corresponding to regions in the US
us_sites = all_sites_soup.body.section.div.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling

# Extract HTML tags corresponding to the state name and region
states_tags = us_sites.find_all('h4')
regions_tags = us_sites.find_all('ul')

# %%
# Create dictionary which maps a state_name (key) to a list of regions in that state (values)
state_to_region_dict = get_state_to_region_dict(states_tags, regions_tags)

# %% [markdown]
# ## Get URL for each individual posting in a state/region combo

# %%
all_urls = process_and_get_urls(state_to_region_dict)

# %%
# # Calculate how many posts in total are to be scraped for countdown timer

# num_regions = len(all_urls)

# num_posts = 0
# for state_and_region in all_urls:
#     num_posts += len(all_urls[state_and_region])

# %% [markdown] tags=[]
# ## Getting soup object response for each individual post in a state/region combo

# %%
soup_objects = convert_urls_to_soup_objs(all_urls)

# %% [markdown]
# ## Pre-Processing
#
# ### Extracting post information from each soup_object

# %%
concat_df = extract_post_features(soup_objects)

# %% [markdown]
# ### Adding more detailed location information from US Census data

# %%
# # Add US_region division for eastern us, western us, etc., using census data to classify each region

# census_regions = pd.read_csv('./census-regions/us_census_regions.csv')
# concat_df_w_regions = concat_df.merge(right=census_regions[['State','Region','Division']], how='left', left_on='state', right_on='State')

# concat_df_w_regions.drop(labels='State', axis=1, inplace=True)
# concat_df_w_regions.rename(columns={'Region':'US_region', "Division":"US_division"}, inplace=True)

# concat_df_w_regions.head()

# %%
# concat_df_w_regions[concat_df_w_regions['US_region'].isna()==True]

# %% [markdown]
# ### Dropping Duplicate posts

# %%
# Count duplicates.
concat_df['post_text'].duplicated().value_counts()

# %%
df_exact_txt_dropped = drop_exact_duplicates(concat_df)

# %% [markdown]
# ### Dropping posts that are above a certain similarity threshold.  
#
# Many posts on Craigslist are from the same person, who changes the text of the post slightly to avoid being flagged and removed.  If a post has a similarity_ratio of 1, it's identical to another post in the df.  All posts with a similarity_ratio >= similarity threshold will be dropped.  In theory, this should leave us with a df that has no more duplicates of any kind and each row represents a unique post.

# %%
df_similar_txt_dropped = drop_posts_with_similar_text(df_exact_txt_dropped, similarity_threshold=0.63)

# %% [markdown]
# ### Dropping posts that contained no prices, which aren't helpful for our analysis

# %%
df_with_prices = drop_posts_without_prices(df_similar_txt_dropped)

# %%
unique_posts_count = len(df_similar_txt_dropped)
post_with_prices_count = len(df_with_prices)
num_posts = len(concat_df)

percent_unique = unique_posts_count / num_posts * 100
percent_with_prices = post_with_prices_count / num_posts * 100

print(F"Out of {num_posts} posts, there were {unique_posts_count} that were unique, or {percent_unique:.2f}%.")
print(F"Out of those, there were {post_with_prices_count} posts that had prices included.")

print(F"Only {percent_with_prices:.2f}% of the posts that we scraped remain.")

# %% [markdown]
# ### Extracting complete.

# %% [markdown] tags=[]
# # *Transforming* Craigslist data: Post-processing

# %% [markdown] tags=[]
# ## Are there any posts that might need manual cleaning?  This would include:
# * Posts that had 3 or more prices and `price` was marked as null
# * Posts where the price wasn't able to convert from `str` -> `int` and `price` was marked as null during pre-processing
#
# There are the entries that were marked as `Null`.  Let's investigate them manually:

# %%
df_null_prices = df_with_prices[df_with_prices['price'].isnull()==True]
#df_null_prices[['price', 'price_list']]

# %%
posts_with_mult_prices = df_null_prices.shape[0]
print(F"There were {posts_with_mult_prices} posts with price marked null.")

# %%
# Store posts with null prices to CSV to manually inspect later

date_of_html_request = str(dt.date.today())

#df_null_prices = df_null_prices.drop(columns=['len_of_price_list'])
df_null_prices.to_csv('./posts_to_investigate/{}_posts_with_null_prices.csv'.format(date_of_html_request), index=False)

# %%
# Inspect links manually, one by one, to decide what to do about price information
with pd.option_context('display.max_colwidth', None):
  x=3
  #display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['link'])
  display(df_with_prices.iloc[x]['price'])

# %% [markdown]
# ### Cleaning posts with three or more prices manually - distilling down to one price
#
# We distill posts that had more complicated text that involved three or more prices, such as :
#
# * $40$/hr, $50$/1.5hr, $60$/2hr
#   * Complicated pricing schedule
# * $40$/hr but $10$ additional per person, if a group session is desired
#   * Group rates
# * $30$/hr Science, $40$/hr math, come and try a first session for the reduced price of $20$.
#   * Special offers
#
# into a single price.  Other posts repeated their prices multiple times, so we distill those down to a single price as well.

# %%
df_with_prices= clean_3_plus_prices(df_with_prices)

# %% [markdown] tags=[]
# #### Checking results - Are there any posts that were marked as needing to be cleaned that we missed?

# %%
num_still_null = len(df_with_prices[df_with_prices['price'].isnull()==True])

if num_still_null==0:
    print("There are no posts with null prices still needing cleaning.")
else:
    print(F"There are {num_still_null} posts that need cleaning.")

# %% [markdown]
# ### Checking Posts that have two prices listed to see if averaging them is reasonable

# %%
df_with_prices[df_with_prices['len_of_price_list']==2][['price','price_list']]

# %%
# Inspect posts manually, one by one
with pd.option_context('display.max_colwidth', None):
  x=136
  #display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['link'])
  display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['price'])

# %% [markdown]
# #### Manually cleaning certain postings that had two prices listed
#
# While averaging is helpful for some posts, it doesn't apply to all of them.  The clean_two_prices() function is meant to update our data with correct pricing information in the posting where using an average to deal with the two prices in the post isn't ideal.

# %%
df_with_prices = clean_two_prices(df_with_prices)

# %% [markdown]
# ## Investigating posts with extreme prices.  Are there any price outliers that we need to clean?
#
# Prices >= 100 or <= 20 are what I would consider to be extreme prices.  Let's investigate them.

# %%
df_with_prices[(df_with_prices['price']>=100) | (df_with_prices['price']<=20)][['price', 'post_text', 'price_list']] 

# %%
# Manually inspect these posts one by one
with pd.option_context('display.max_colwidth', None):
  x=40
  #display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['link'])
  display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['price'])

# %% [markdown] tags=[]
# ### Dropping posts with extreme prices that aren't relevant

# %%
# This ad is for poker tutoring/coaching, not really what I'm competing against, so we drop it.  He also mentions he tutors math in this post, but he has a separate post, that we've captured, which has his math tutoring pricing information.
australia_daniel_idx = df_with_prices[df_with_prices['post_text'].str.contains("I'm available as a dealer if you need one", regex=False)==True].index

df_with_prices.drop(labels=australia_daniel_idx, inplace=True)
df_with_prices = df_with_prices.reset_index(drop=True)

# %% [markdown]
# ### Correcting pricing information for posts with extreme prices

# %%
# This ad says $50/hr but then mentions a prepay plan for $160 for 4 hours.  Since these are the only two prices in the post, our code averages them, so we set the correct price to $50
google_maps_idx = df_with_prices[df_with_prices['post_text'].str.contains("willing to travel if Google Maps", regex=False)==True].index

try:
    df_with_prices.iloc[google_maps_idx, price_col_idx] = 50

except:
    print("Issue with google_maps_idx and iloc.")
    pass 

# %%
# This ad says $45/hr for high school or college, but then mentions a $35 for middle school.  Since these are the only two prices in the post, our code averages them, so we set the correct price to $45, since I primarily tutor high school or college students.
rancho_penasquitos_idx = df_with_prices[df_with_prices['post_text'].str.contains("Rancho Penasquitos (Park Village Neighborhood)", regex=False)==True].index

try:
    df_with_prices.iloc[rancho_penasquitos_idx, price_col_idx] = 45

except:
    print("Issue with rancho_penasquitos_idx and iloc.")
    pass 

# %% [markdown]
# ### Transforming Complete

# %% [markdown] tags=[]
# # *Load* - Saving results
#
# ### Store results locally as CSV files

# %%
date_of_html_request = str(dt.date.today())

# Drop unnecessary columns.
df_for_sql = df_with_prices.drop(labels=['link', 'price_list', 'len_of_price_list'], axis=1)

# In order for psycopg2 to parse our CSV file correctly later, we need to escape all new line characters by adding an additional \ in front of \n.
df_for_sql['post_text'] = df_for_sql['post_text'].str.replace('\n', '\\n')

# Store cleaned data as CSV file in preparation for importing to SQL database
df_for_sql.to_csv("./csv_files/{}_all_regions_with_prices.csv".format(date_of_html_request), index=False, sep=';')

# Store original data, before we applied any cleaning to it, in case it's needed for something later on.
concat_df.to_csv("./csv_files/{}_all_regions_posts.csv".format(date_of_html_request), index=False)

# %%
df_similar_txt_dropped.to_csv('./csv_files/{}_all_regions_no_dups.csv'.format(date_of_html_request), index=False, sep=';')

# %% [markdown]
# ### Importing into PostgreSQL database

# %%
# Establish connection to PSQL database
conn = psycopg2.connect("host=localhost dbname=rancher user=rancher port=5430")

# Instantiate a cursor object
cur = conn.cursor()

# Use cursor object to create a database for storing the information we scraped and cleaned, if one doesn't already exist.
cur.execute("""    
    CREATE TABLE IF NOT EXISTS cl_tutoring(
    id SERIAL primary key,
    date_scraped date,
    price decimal,
    city text,
    subregion text,
    region text,
    state text,
    post_text text,
    date_posted timestamp
);
""")

# Commit changes to database
conn.commit()

# %%
# Instantiate a new cursor object
cur = conn.cursor()

# Copy data from our CSV file into database.  
### Note, we can use the ; separator freely because we replaced all instances of semicolons in post_text to commas during the preprocessing stage, ensuring that psycopg2 won't misinterpret a semicolon in the body of a post as a separator.
### Also, we must specify null="" because Python represents null values as an empty string when writing to a CSV file and psycopg2 needs to know how null values are represented in the CSV file in order to properly insert null values into the database
with open('./csv_files/' + str(date_of_html_request) + '_all_regions_with_prices.csv', 'r') as file:
    next(file) # Skip the header row
    cur.copy_from(file, 'cl_tutoring', sep=';', null="", columns=('date_posted', 'price', 'city', 'subregion', 'region', 'state', 'post_text', 'date_scraped'))
    
# Commit changes to database
conn.commit()

# %% [markdown]
# ### Done!!!

# %%
