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
# from requests import get
# import requests
# from requests.packages.urllib3.util.retry import Retry
# from requests.adapters import HTTPAdapter
# import random
# from bs4 import BeautifulSoup
# import re
# import numpy as np
# import csv 
# import time
# from sklearn.feature_extraction.text import TfidfVectorizer

# %%
import pandas as pd
import datetime as dt
import psycopg2

from helper_funcs.urls_to_soup_objects import *
from helper_funcs.clean_three_or_more_prices import *
from helper_funcs.clean_two_prices import *
from helper_funcs.soup_objects_to_df import *
from helper_funcs.dropping_funcs import *
from helper_funcs.update_prices import *

# %% [markdown]
# # *Extract* Craigslist Data

# %% [markdown]
# ## Get all state/region names

# %%
states_tags, regions_tags = get_state_and_region_tags()

# %%
# Create dictionary which maps a state_name (key) to a list of regions in that state (values)
state_to_region_dict = get_state_to_region_dict(states_tags, regions_tags)

# %% [markdown]
# ## Get URL for each individual posting in a state/region combo

# %%
all_urls = process_and_get_urls(state_to_region_dict)

# %% [markdown] tags=[]
# ## Getting soup object response for each individual post in a state/region combo

# %% tags=[]
soup_objects = convert_urls_to_soup_objs(all_urls)

# %% [markdown]
# ## Scraping post information from each soup_object

# %%
df_all_posts = extract_post_features(soup_objects)

# %% [markdown]
# # *Transform* Craigslist data
# ## Pre-Processing

# %% [markdown]
# ### Adding more detailed location information from US Census data

# %%
# # Add US_region division for eastern us, western us, etc., using census data to classify each region

# census_regions = pd.read_csv('./census-regions/us_census_regions.csv')
# df_all_posts_w_regions = df_all_posts.merge(right=census_regions[['State','Region','Division']], how='left', left_on='state', right_on='State')

# df_all_posts_w_regions.drop(labels='State', axis=1, inplace=True)
# df_all_posts_w_regions.rename(columns={'Region':'US_region', "Division":"US_division"}, inplace=True)

# df_all_posts_w_regions.head()

# %%
# df_all_posts_w_regions[df_all_posts_w_regions['US_region'].isna()==True]

# %% [markdown]
# ### Dropping posts

# %% [markdown]
# #### Dropping Duplicate posts

# %%
df_exact_txt_dropped = drop_exact_duplicates(df_all_posts)

# %% [markdown] tags=[]
# #### Dropping posts that are above a certain similarity threshold.  
#
# Many posts on Craigslist are from the same person, who changes the text of the post slightly to avoid being flagged and removed.  If a post has a similarity_ratio of 1, it's identical to another post in the df.  All posts with a similarity_ratio >= similarity threshold will be dropped.  In theory, this should leave us with a df that has no more duplicates of any kind and each row represents a unique post.

# %%
df_similar_txt_dropped = drop_posts_with_similar_text(df_exact_txt_dropped, similarity_threshold=0.63)

# %% [markdown]
# #### Dropping posts that contained no prices, which aren't helpful for our analysis

# %%
df_with_prices = drop_posts_without_prices(df_similar_txt_dropped)

# %% [markdown]
# ### Pre-Processing complete - Summary:

# %%
unique_posts_count = len(df_similar_txt_dropped)
post_with_prices_count = len(df_with_prices)
num_posts = len(df_all_posts)

percent_unique = unique_posts_count / num_posts * 100
percent_with_prices = post_with_prices_count / num_posts * 100

print(F"Out of {num_posts} posts, there were {unique_posts_count} that were unique, or {percent_unique:.2f}%.")
print(F"Out of those, there were {post_with_prices_count} posts that had prices included.")

print(F"Only {percent_with_prices:.2f}% of the posts that we scraped remain.")

# %% [markdown] tags=[]
# ## Post-processing

# %%
# Inspect links manually, one by one, to decide what to do about price information
with pd.option_context('display.max_colwidth', None):
  x=3
  #display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['link'])
  display(df_with_prices.iloc[x]['price'])

# %% [markdown] tags=[]
# ### Cleaning posts that have a null `price`.  

# %% [markdown]
# #### Cleaning posts with three or more prices - distilling down to one price
#
# When a post has three or more prices, our script marked the `price` as null to be dealt with later.  Here, I distill posts that had more complicated text that involved three or more prices into a single price, such as :
#
# * $40$/hr, $50$/1.5hr, $60$/2hr
#   * Complicated pricing schedule
# * $40$/hr but $10$ additional per person, if a group session is desired
#   * Group rates
# * $30$/hr Science, $40$/hr math, come and try a first session for the reduced price of $20$.
#   * Special offers
#
# Other posts repeated their prices multiple times, so we distill those down to a single price as well.

# %%
df_with_prices = clean_three_or_more_prices(df_with_prices)

# %% [markdown] tags=[]
# #### Checking results - Are there any posts with a `price` that was marked null that we missed?

# %%
num_still_null = len(df_with_prices[df_with_prices['price'].isnull()==True])

if num_still_null==0:
    print("There are no posts with null prices still needing cleaning.")
else:
    print(F"There are {num_still_null} posts with a null price that need cleaning.")

# %% [markdown] tags=[]
# ##### This section if for if we want to inspect these objects manually right now.

# %%
# Manually inspect these posts one by one
with pd.option_context('display.max_colwidth', None):
  x=40
  #display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['link'])
  display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['price'])

# %% [markdown] tags=[]
# #### Storing rows with null prices as CSV for inspection later
# There are the entries that have a price still marked as `Null`.  We'll store them as a csv file to inspect later:

# %%
df_null_prices = df_with_prices[df_with_prices['price'].isnull()==True]
#df_null_prices[['price', 'price_list']]

posts_with_mult_prices = df_null_prices.shape[0]
print(F"There were {posts_with_mult_prices} posts with price marked null.")

# %%
# Store posts with null prices to CSV to manually inspect later

date_of_html_request = str(dt.date.today())

#df_null_prices = df_null_prices.drop(columns=['len_of_price_list'])
df_null_prices.to_csv('./csv_files/posts_to_investigate/{}_posts_with_null_prices.csv'.format(date_of_html_request), index=False)

# %% [markdown]
# ### Checking posts that have two prices listed.  Is averaging them reasonable?

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
# ### Investigating posts with unusual prices.  Are there any price outliers that we need to clean?
#
# Prices >= 100 or <= 20 are what I would consider to be unusual prices.  Let's investigate them.

# %%
df_with_prices[(df_with_prices['price']>=100) | (df_with_prices['price']<=20)][['price', 'post_text', 'price_list']] 

# %% [markdown] tags=[]
# #### This section if for if we want to inspect these objects manually right now.

# %%
# Manually inspect these posts one by one
with pd.option_context('display.max_colwidth', None):
  x=40
  #display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['link'])
  display(df_with_prices.iloc[x]['post_text'])
  display(df_with_prices.iloc[x]['price'])

# %% [markdown]
# #### Correcting pricing information for posts with unusual prices

# %%
df_with_prices = update_prices(df_with_prices)

# %% [markdown] tags=[]
# ### Dropping posts with that aren't relevant

# %%
# This ad is for poker tutoring/coaching, not really what I'm competing against, so we drop it.  He also mentions he tutors math in this post, but he has a separate post, that we've captured, which has his math tutoring pricing information.
australia_daniel_idx = df_with_prices[df_with_prices['post_text'].str.contains("I'm available as a dealer if you need one", regex=False)==True].index

df_with_prices.drop(labels=australia_daniel_idx, inplace=True)
df_with_prices = df_with_prices.reset_index(drop=True)

# %% [markdown]
# ## Transforming Complete

# %% [markdown] tags=[]
# # *Load* Craigslist data
#
# ## Saving results - Store results locally as CSV files

# %%
date_of_html_request = str(dt.date.today())

# Drop unnecessary columns.
df_for_sql = df_with_prices.drop(labels=['link', 'price_list', 'len_of_price_list'], axis=1)

# In order for psycopg2 to parse our CSV file correctly later, we need to escape all new line characters by adding an additional \ in front of \n.
df_for_sql['post_text'] = df_for_sql['post_text'].str.replace('\n', '\\n')

# Store cleaned data as CSV file in preparation for importing to SQL database
df_for_sql.to_csv("./csv_files/posts_with_prices/{}_all_regions_with_prices.csv".format(date_of_html_request), index=False, sep=';')

# Store original data, before we applied any cleaning to it, in case it's needed for something later on.
df_all_posts.to_csv("./csv_files/full_posts/{}_all_regions_posts.csv".format(date_of_html_request), index=False)

# %%
df_similar_txt_dropped.to_csv('./csv_files/unique_posts/{}_all_regions_no_dups.csv'.format(date_of_html_request), index=False, sep=';')

# %% [markdown]
# ## Importing into PostgreSQL database

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
with open('./csv_files/posts_with_prices/' + str(date_of_html_request) + '_all_regions_with_prices.csv', 'r') as file:
    next(file) # Skip the header row
    cur.copy_from(file, 'cl_tutoring', sep=';', null="", columns=('date_posted', 'price', 'city', 'subregion', 'region', 'state', 'post_text', 'date_scraped'))
    
# Commit changes to database
conn.commit()

# %% [markdown]
# # Done!!!

# %%
