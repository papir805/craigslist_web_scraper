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

from helper_funcs.helper_funcs import *
from helper_funcs.clean_three_or_more_prices import *
from helper_funcs.clean_two_prices import *

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

# %% [markdown]
# ## Get URL for each region of Craigslist

# %%
state_to_region_dict = get_state_to_region_dict(states_tags, regions_tags)

# %%
# states_and_regions = list(zip(states_tags, regions_tags))

# # For each of the HTML tags, we get the text of which state the region belonged to and the text of the region's name.  We now have a dictionary with keys as states that map to a list of regions in that state
# state_dict = {}

# for ele in states_and_regions:
#     current_state = ele[0].text
#     href_list = ele[1].find_all('li')
#     temp_region_list = []
#     for href in href_list:
#         region = href.a['href'].replace('https://','').replace('.craigslist.org/','')
#         temp_region_list.append(region)
#         state_dict[current_state]=temp_region_list

# %% [markdown]
# ## Crawl each state/region of Craigslist
# Get the URL that corresponds to a search of the services section for "math tutor."  Craigslist is limited to showing 120 results per page, so if a region has more than 120 postings, we extract URLs corresponding to the next page of results, until there is no next button anymore and we've extracted all URLs for that region.

# %%
# import itertools

# test_dict = dict(itertools.islice(state_to_region_dict.items(), 2))

# %% tags=[]
# search_page_url_dict = get_region_search_pg_urls(state_to_region_dict)

# %%
all_urls = process_and_get_urls(state_to_region_dict)

# %% tags=[]
# # Walk through each state in our state_Dict to get the HTML page corresponding to a search for "math tutor" in the services section
# response_dict = {}

# for state in state_dict.keys():

#     for region in state_dict[state]:
#         # This gets the first page of search results
#         i=1
        
#         current_response = session.get('https://' + region + '.craigslist.org/d/services/search/bbb?query=math%20tutor&sort=rel')
        
#         sleep_timer = random.randint(2,4)
#         time.sleep(sleep_timer)
        
#         print(F"Response #{i} for {state}: {region} received.")
#         #print(F"Waiting {sleep_timer} seconds...")
#         #print()
        
#         region_response_list = []
#         region_response_list.append(current_response)

#         # This gets all subsequent pages, using the next button from the search page
#         is_next_button = True
#         while is_next_button:
#             try:
#                 next_response = current_response
#                 next_soup = BeautifulSoup(next_response.text, 'html.parser')
                
# # CL search pages have one of the following:
#     # 1) A next button:
#         # - when the region contains more than 120 posts for a given search
#     # 2) A greyed out next button:
#         # - when you've reached the last page of search results and there are no more
#         # OR
#         # - when a page has less than 120 results.
#     # 3) No next button:
#         # - when a page has less than 120 results
# # html suffix is None type when a next button isn't shown
# # html suffix is '' when the next button is greyed out.  This can happen in either case 2) or 3) from above
# # The while loop only needs to be peformed in case 1) when there is a next button you can click
#                 html_suffix = next_soup.find(class_='button next')
#                 #print(html_suffix)
#                 if html_suffix is not None:
#                     html_suffix = html_suffix.get('href')
#                     #print("html_suffix is not none")
#                     if html_suffix != '':
#                         i += 1
#                         #print(i, html_suffix)
#                         #print('html_suffix is not blank')
#                         new_button = 'https://' + region + '.craigslist.org' + html_suffix
#                         current_response = session.get(new_button)
#                         region_response_list.append(current_response)

#                         sleep_timer = random.randint(2,4)
#                         time.sleep(sleep_timer)
#                         print(F"{region} {i} response received.")
#                         print(F"Waiting {sleep_timer} seconds...")
#                         print()
#                     else:
#                         is_next_button = False
#                         #print('html_suffix is blank')
#                         print(F"Last response for {region} received.  Process completed.")
#                         print()
#                 else:
#                     is_next_button = False
#                     #print('next_button is None')
#                     print(F"Last response for {region} received.  Process completed.")
#                     print()
#                     pass
#             except:
#                 is_next_button = False
#                 pass

#         # Store all search pages for math tutor
#         response_dict[(state, region)] = region_response_list

# %% [markdown]
# ## Get URL for each individual posting in a state/region combo

# %%
# # Walk through each state/region combo to get a list of all individual postings for math tutoring in the results pages we searched up earlier.
# posts_dict = {}
# for key, responses in response_dict.items():
#     state = key[0]
#     region = key[1]
#     #current_region = region
#     region_posts = []
#     for response in responses:
#         current_html_soup = BeautifulSoup(response.text, 'html.parser')
#         current_posts = current_html_soup.find_all('li', class_='result-row')
#         wanted_posts = []
#         for post in current_posts:
# # Many CL pages have "results from nearby areas", for instance some results for sandiego.craigslist.org show up in the losangeles.craigslist.org.  By comparing the region that we're currently scraping from against the URL of the posts, we can detect if it's from a nearby region or not.  To avoid duplicates and make the script finish more quickly, We only want to include posts where the URL of the post matches the region we're scraping from
#             if post.a.get('href').replace('https://','').split('.')[0] == region:
#                 wanted_posts.append(post)
#         region_posts.extend(wanted_posts)
#     posts_dict[(state,region)] = region_posts

# %%
# # %store

# %%
# # %store -r

# %%
# urls_of_posts_dict = get_urls_of_posts(search_page_url_dict)

# %%
# Calculate how many posts in total are to be scraped for countdown timer

num_regions = len(all_urls)

num_posts = 0
for state_and_region in all_urls:
    num_posts += len(all_urls[state_and_region])

# %%
soup_objects = convert_urls_to_soup_objs(all_urls)

# %% [markdown] tags=[]
# ## Getting soup object response for each individual post in a state/region combo

# %% tags=[]
# soup_objects_dict = {}

# num_posts_remaining = num_posts
# current_time = dt.datetime.now()
# max_seconds_until_finish = num_posts * 4
# max_finish_time = current_time + dt.timedelta(seconds=max_seconds_until_finish)

# print(F"Current time is {current_time.strftime('%H:%M:%S')}")
# print(F"Process estimated to finish before {max_finish_time.strftime('%H:%M:%S')}")
# print()

# for count, key in enumerate(posts_dict, start=1):
#     # Walk through each region and create a list of soup_objects to scrape from by storing them into memory.  This way we only have to send these get requests once and Craigslist doesn't ban us for sending the same https requests over and over
#     soup_objects_list = []
#     for i, post in enumerate(posts_dict[key]):
        
#         # Impose a timer to help prevent from getting banned for too many HTTP requests in too short a time period.
#         random_int = random.randint(2,4)
#         time.sleep(random_int)
#         current_link = post.a.get('href')
#         response_object = session.get(current_link)
#         soup_object = BeautifulSoup(response_object.text, 'html.parser')
#         soup_objects_list.append(soup_object) 
        
#         # Impose condition that every 10th post will trigger something printed to the screen.  This part of the code is a long process and I wanted something to help keep track of how much progress has been made
#         if (i !=0) and ((i-1) % 10 == 9):
#             print(F"Post number {i} in {key} is being extracted.")
    
#     soup_objects_dict[key] = soup_objects_list
#     if count != len(posts_dict):
#         num_posts_remaining -= len(posts_dict[key])
#         current_time = dt.datetime.now()
#         new_seconds_until_finish = num_posts_remaining * 5
#         new_max_finish_time = current_time + dt.timedelta(seconds=new_seconds_until_finish)
        
#         state = key[0]
#         region = key[1]
        
#         print(F"Soup objects for {state}: {region} acquired.  Waiting for next region...")
#         print(F"Process will now finish by {new_max_finish_time.strftime('%H:%M:%S')}")
#         print()
#     else:
#         print()
#         print(F"Soup objects for {key} acquired.  Process complete.")

# %% [markdown]
# ## Pre-Processing
#
# ### Extracting information from each post

# %% tags=[]
# df_list = []
# error_list_text = []
# error_list_links = []

# # Walk through lists of soup objects corresponding to an individual posting for a math tutor in a given search_region.
# for search_region in soup_objects_dict:
#     # Initialize several lists to store relevant information for analysis
#     price_list = []
#     city_list = []
#     datetime_list = []
#     body_text_list = []
#     subregion_list = []
#     region_list = []
#     link_list = []
#     search_region_price_list = []
#     state_list = []
    
#     # Walk through each soup object in the list corresponding to the search region
#     for soup in soup_objects_dict[search_region]:
#         try:
#             # Get link of post
#             link = soup.find("meta", property="og:url")['content']
#         except:
#             # In case a link can't be found, we add the soup object to a list to inspect later and set link to 'None', which we'll use as a filter later so Python doesn't try to scrape from them.  Without a link, we don't want to scrape though, so we pass to the next iteration of the loop.
#             link = 'None'
#             error_list_links.append(soup)
#             pass
#             #print("Couldn't get link")
            
#         try:
#             # Extract region of post from Craigslist
#             post_region = soup.find_all('li',class_='crumb area')[0].find('a').get_text()
#             if post_region=='sf bay area':
#                 post_region = 'sfbay'
#             else:
#                 post_region = post_region.replace(' ', '')
#             post_region = post_region.lower()
            
#         except:
#             post_region = 'region not found'
        
#         # Get text of postingbody of the post and remove unwanted text.
#         try:
#             text = soup.find('section', id='postingbody').get_text()
#             text = text.replace(u'\xa0', u' ')
#             # We do this so that we can use ; as a delimiter when copying data from a CSV file into a SQL database later.
#             text = text.replace(';', ',') 
#             # We do this because one post in particular had this text and was giving me trouble.  The best way I could find to handle it was to remove the text.
#             text = text.replace('QR Code Link to This Post', '') 

#         except:
#             error_list_text.append(soup)
#             text = 'text not found'
#             #body_text_list.append(text)
#             #print("Couldn't get text")
            
#         state = search_region[0]
#         state_list.append(state)
#         region_list.append(post_region)
#         link_list.append(link)
#         body_text_list.append(text)

#         # Use regular expressions to find all instances of prices in the text
#         #old_prices = re.findall('(?:[\$]{1}[,\d]+.?\d*)', text)
#         old_prices = re.findall('(?:[\$]{1}[,\d]+\d*)', text)
#         # Alternative, if trying to capture decimals 
#         # ^(?:\${1}\d+(?:,\d{3})*(?:\.{1}\d{2}){0,1})?$

#         # Intialize empty list to store the new prices after processing old prices.
#         new_prices = []
#         #print(F"Initialized new_prices: {new_prices}")
        
#         #Walk through each price in the post.
#         for price in old_prices:
#             # Clean unwanted characters.
#             price = price.replace('$', '')
#             price = price.replace('/', '')
#             price = price.replace('!', '')
#             price = price.replace('h', '')
#             price = price.replace('.', '')
#             price = price.replace(')', '')
#             price = price.replace(',', '')
#             price = price.replace('>', '')
#             price = price.rstrip()   
#             # Some tutors give prices as a range ie '$30-40'.  In order to work with this data, I split based on the hyphen, then I can use each price individually.
#             split_prices = price.split('-')
#         #print(F"Here are the old_prices: {old_prices}")
#         #print(F"Here are the split_prices: {split_prices}")

#             # Walk through the split price, if a price had no hypen, the split_prices has one price in it that we perform processing on.  If a hyphen was present, then we have multiple prices that we iterate over and process
#             for p in split_prices:
#                 # Only proceed if the post contained prices, ie if p is a non-empty string.
#                 if len(p)!=0:
#                     try:
#                         # Convert string price to int.
#                         new_int = int(p)
#                         # Ignore prices which are too high to be reasonable.  Some posts included scholarship amounts as ways for a tutor to boast about their abilities, but this will only allow dollar amounts that are reasonable through.
#                         if new_int <= 200:
#                             new_prices.append(new_int)

#                     except:
#                         # Show which prices aren't able to convert to an int and the post they came from so we can isolate and fix the issue if need be.
#                         print(F'Error converting this price: {p}')
#                         print(split_prices)
#                         print()
#                         print('Here is the text of the post:')
#                         print()
#                         print(text)
#                         print('-'*50)
#                         print()
#                         # Set prices that can't be covered to NaN so the process can finish.
#                         new_prices.append(np.nan) 
#         #print(F"Here are the processed new_prices: {new_prices}")
#                 #print(len(new_prices))


#         # Append all prices from the post to a separate list, in case we need to isolate issues and fix them later.

#         search_region_price_list.append(new_prices)

#         # For posts that had no prices listed, we use null
#         if len(new_prices)==0:
#             price_list.append(np.nan)
#         # For posts that had a single price, we use it.
#         elif len(new_prices)==1:
#             price_list.append(new_prices[0])
#         # For posts that contained two prices, we average them.  This isn't a perfect system but is mainly targeted to posts that give a range of prices (ie $25-30).
#         elif len(new_prices)==2:
#             avg_price_2 = np.average(new_prices)
#             price_list.append(avg_price_2)
#         # If a post has more than 3 prices, we append null.  We'll have to inspect these posts manually and deal with them later.
#         else:
#             price_list.append(np.nan)
#         #print(price_list)


#         # Get city information for each posting.
#         try:
#             city = soup.find(class_='postingtitletext').small.get_text()

#             # Because of the way CL operates, one has to choose a city from a radio button list, that CL provides, when one creates a post to offer a service, however later, there's a field where they can type in any city they want.  Many people will randomly choose a city from the radio button list, but then  post their city as "online".  This makes sure we capture them. 
#             re_pattern = re.compile('online')
#             online_flag = re.search(re_pattern, city.lower())
#             if online_flag:
#                 city_list.append('Online')
#             else:
#                 # Strip out leading and trailing white spaces, replace parentheses, and capitalize each word in the str.
#                 city = city.strip()
#                 city = city.replace('(', '').replace(')', '')        
#                 city = city.title()
#                 city_list.append(city)
#         except:
#             # If a post has no city information, use None
#             city_list.append('no city found')

#         # Extract subregion of Craigslist that the post was made in. This will allow for comparison of prices across different cities within the same metropolitan sub_region.
#         try:
#             subregion = soup.find_all('li', class_='crumb subarea')[0].find('a').get_text()
#             subregion = subregion.title()
#             subregion_list.append(subregion)
#         except:
#             subregion_list.append('no subregion found')


#         # Extract time the posting was made.
#         try:
#             dt_object = soup.find('time')['datetime']
#             datetime_list.append(dt_object)
#         except:
#             datetime_list.append('time of post unavailable')
#     # else:
#     #     pass
#     #print(price_list)
#     # Create temporary df to store results for each region
#     temp_df = pd.DataFrame(data=zip(datetime_list,
#                                     link_list, 
#                                     price_list, 
#                                     city_list, 
#                                     subregion_list, 
#                                     region_list,
#                                     state_list,
#                                     body_text_list,
#                                     search_region_price_list),
#                         columns=['date_posted', 
#                                  'link', 
#                                  'price', 
#                                  'city', 
#                                  'subregion', 
#                                  'region',
#                                  'state',
#                                  'post_text',
#                                  'price_list']
#                           )
#     df_list.append(temp_df)

# %%
# # Check for errors in getting text from a post, or from getting the URL of a post.
# len(error_list_text), len(error_list_links)

# %%
# # Concatenate the dfs for each region into one larger df and check its shape.
# concat_df = pd.concat(df_list, ignore_index=True)
# concat_df.shape

# %%
concat_df = extract_post_features(soup_objects)

# %%
# concat_df = extract_post_features(soup_objects_test_dict)

# %%
# # Add US_region division for eastern us, western us, etc., using census data to classify each region

# census_regions = pd.read_csv('../craigslist_web_scraper/census-regions/us_census_regions.csv')
# concat_df_w_regions = concat_df.merge(right=census_regions[['State','Region','Division']], how='left', left_on='state', right_on='State')

# concat_df_w_regions.drop(labels='State', axis=1, inplace=True)
# concat_df_w_regions.rename(columns={'Region':'US_region'}, inplace=True)

# concat_df_w_regions.head()

# %%
# concat_df_w_regions[concat_df_w_regions['Region'].isna()==True]

# %% [markdown]
# ### Dropping Duplicate posts

# %%
# # Get date of html request to label our output with.
# date_of_html_request = str(dt.date.today())

# # Include the date posts were scraped on to track tutoring prices over time.
# concat_df['posts_scraped_on'] = date_of_html_request

# Count duplicates.
concat_df['post_text'].duplicated().value_counts()

# %%
df_exact_txt_dropped = drop_exact_duplicates(concat_df)

# %%
# # Find indices of rows that have exactly the same post_text, then drop them and reset indices.
# duplicate_indices = concat_df[concat_df['post_text'].duplicated()==True].index
# df_exact_txt_dropped = concat_df.drop(index=duplicate_indices)
# df_exact_txt_dropped = df_exact_txt_dropped.reset_index(drop=True)
# df_exact_txt_dropped['len_of_price_list']=df_exact_txt_dropped['price_list'].apply(lambda x: len(x))
# df_exact_txt_dropped.shape

# %%
# # Vectorize each posts' text and calculate the cosine similarity of each post against all other posts to determine which are duplicates
# ## https://kanoki.org/2018/12/27/text-matching-cosine-similarity/
# text_for_comparison = df_exact_txt_dropped['post_text']
# vect = TfidfVectorizer(min_df=1, stop_words='english')
# tfidf = vect.fit_transform(text_for_comparison)
# pairwise_similarity = tfidf * tfidf.T

# # Store results in a 2D NumPy array
# pairwise_array = pairwise_similarity.toarray()

# # The diagonal of our array is the similarity of a post to itself, which we fill will null so that these are essentially ignored
# np.fill_diagonal(pairwise_array, np.nan)

# # Many people on CL will change their posting in ways to avoid CL flagging them as duplicates for removal.  This finds all posts above a certain similarity threshold.
# argwhere_array = np.argwhere(pairwise_array > 0.63)

# %% tags=[]
# # In order to remove the duplicates, we need to restructure our 2D NumPy array in such a way that the first column is the index of the post that has a duplicate and the second column contains a list of the indices of the duplicate post(s).
# df_row_idx = []
# dup_row_idx = []
# for row in argwhere_array:
#     current_idx = row[0]
#     #print(F"Current row: {row}, Current idx: {current_idx}")
#     duplicate_list = []
#     if current_idx in df_row_idx:
#         continue
#     else:
#         df_row_idx.append(current_idx)
#     for other_row in argwhere_array:
#         other_idx = other_row[1]
#         #print(F"Here's the other_row: {other_row}, Other idx: {other_idx}")
#         if current_idx == other_row[0]:
#             duplicate_list.append(other_idx)
#     #print(F"This is the current dup_list: {duplicate_list}")
#     #print()
#     dup_row_idx.append(duplicate_list)
# #list(zip(df_row_idx, dup_row_idx))

# %%
# # Create match column in our df, which is initialized as a list of all indices in our df.  This means for each row, the value of the match column is the row index.  Convert that index value to a list, so we can iterate over it in future steps
# df_exact_txt_dropped['match'] = np.array(df_exact_txt_dropped.index.values, dtype='object')
# df_exact_txt_dropped['match'] = df_exact_txt_dropped['match'].apply(lambda x: [x])

# # For rows that are duplicate postings, we overwrite the value of match column to contain the indices of all other rows that contain duplicated text
# match_col_idx = df_exact_txt_dropped.columns.get_loc('match')
# df_exact_txt_dropped.iloc[df_row_idx, match_col_idx] = dup_row_idx
# #df_exact_txt_dropped['match'] = df_exact_txt_dropped['match'].apply(lambda x: [x])

# df_exact_txt_dropped['match']

# %%
# indices = []

# df_no_dups = df_exact_txt_dropped.copy()

# # Iterate over each row and remove all rows that have duplicated text
# for i, row in df_no_dups.iterrows():
#     indices.append(i)
#     drop_idx = []
#     #print(i, row['match'])
#     try:
#         for item in row['match']:
#             if item not in indices:
#                 drop_idx.append(item)
#         df_no_dups = df_no_dups.drop(index=drop_idx, errors="ignore")
#     except Exception as e:
#         #print(i, item, row['match'])
#         print(e, i, item, row['match'])


# %%

# %%
# # Check shape when we dropped posts with exactly the same post_text against the shape after we dropped text deemed similar by cosine similarity 
# df_exact_txt_dropped.shape, df_no_dups.shape

# %%
df_similar_txt_dropped = drop_posts_with_similar_text(df_exact_txt_dropped, similarity_threshold=0.63)

# %% [markdown]
# ### Dropping posts that contained no prices, which aren't helpful for our analysis

# %%
# # Use the len of price_list to find posts that contained no prices
# df_no_dups['len_of_price_list'] = df_no_dups['price_list'].apply(lambda x: len(x))

# # Filter out results that don't have a price and reset indices.
# df_with_prices = df_no_dups[df_no_dups['len_of_price_list'] > 0]
# df_with_prices = df_with_prices.reset_index(drop=True)

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
# * Posts that had 3 or more prices and were marked as null
# * Posts where the price wasn't able to convert from `str` -> `int` and were marked as null during pre-processing
#
# There are the entries that were marked as `Null`.  Let's investigate them manually:

# %%
df_null_prices = df_with_prices[df_with_prices['price'].isnull()==True]
df_null_prices[['price', 'price_list']]

# %%
posts_with_mult_prices = df_null_prices.shape[0]
print(F"There were {posts_with_mult_prices} posts with price marked null.")

# %%
# Store posts with null prices to CSV to manually inspect later
df_null_prices = df_null_prices.drop(columns=['len_of_price_list'])
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
# price_col_idx = df_with_prices.columns.get_loc('price')

# %%
# # Says $40 for in person, or $45 for at home, so I took the average.
# san_mateo_tutor_idx = df_with_prices[df_with_prices['post_text'].str.contains('I mainly tutor, in person, at the Downtown Redwood City, downtown San Mateo')].index

# try:
#     df_with_prices.iloc[san_mateo_tutor_idx,price_col_idx] = 42.5

# except:
#     print("Issue with san_mateo_tutor and iloc.")
#     pass

# %%
# # Because the ad says $90 in person, $60 for online, and Corona Virus pricing of
# # $40 for online weekdays, I'm using the $40 per hour rate because it seems the
# # most reasonable and is most similar to what I'm competing against.
# kenari_tutor_idx = df_with_prices[df_with_prices['post_text'].str.contains('kenaritutor.com')==True].index

# try:
#     df_with_prices.iloc[kenari_tutor_idx,price_col_idx] = 40
# except:
#     print('Issue with kenari_tutor_idx and iloc.')
#     pass

# %%
# # This ad mentions several prices for different subjects, but explicitly says $30 for math.
# la_honda_idx = df_with_prices[df_with_prices['post_text'].str.contains('909-640-3570')].index

# try:
#     df_with_prices.iloc[la_honda_idx,price_col_idx] = 30
    
# except:
#     print("Issue with la_honda_idx and iloc.")
#     pass

# %%
# # Says #60 per hour.
# glasses_lady_idx = df_with_prices[df_with_prices['post_text'].str.contains("offering virtual one-on-one Math tutoring via Zoom")==True].index

# try:
#     df_with_prices.iloc[glasses_lady_idx, price_col_idx] = 60
# except:
#     print("Issue with glasses_lady_idx and iloc.")
#     pass  

# %%
# # Says #60 per hour.
# UC_Davis_data_scientist = df_with_prices[df_with_prices['post_text'].str.contains("PhD in Engineering from UC Davis")==True].index

# try:
#     df_with_prices.iloc[UC_Davis_data_scientist, price_col_idx] = 60
# except:
#     print("Issue with UC_Davis_data_scientist and iloc.")
#     pass  

# %%
# #This guy has weird price structuring, but I used his hourly rate for each time interval, $100 for 80 minutes, $115 for 100 minutes, $130 for 120 minutes, then averaged those hourly rates to estimate what a single hour would cost.
# oakland_exp_tutor_online_idx = df_with_prices[df_with_prices['post_text'].str.contains('I received a full scholarship to University of Cincinnati and held a 3.8 GPA through my master’s program in aerospace')==True].index

# oakland_tutor_avg_rate = ((100/80) + (115/100) + (130/120)) * 60 / 3

# try:
#     df_with_prices.iloc[oakland_exp_tutor_online_idx, price_col_idx] = oakland_tutor_avg_rate

# except:
#     print("Issue with oakland_exp_tutor_online_idx and iloc.")
#     pass

# %%
# # The ad repeats the price of $40 over and over, so I'm replacing the price with 
# # a single instance.
# star_star_college_math_tutor_idx = df_with_prices[df_with_prices['post_text'].str.contains('https://www.youtube.com/channel/UCqhFZRmUqOAAPMQpo58TV7g'
#                    ) == True].index

# try:
#     df_with_prices.iloc[star_star_college_math_tutor_idx, price_col_idx] = 40
    
# except:
#     print("Issue with star_star_college_math_tutor_idx and iloc.")
#     pass

# %% jupyter={"source_hidden": true} tags=[]
# # Says $50/hr    
# trevor_skelly_idx = df_with_prices[df_with_prices['post_text'].str.contains('trevorskelly')==True].index

# try:
#     df_with_prices.iloc[trevor_skelly_idx,price_col_idx] = 50
    
# except:
#     print("Issue with trevor_skelly_idx and iloc.")
#     pass

# %%
# # Charges $50 per hour for sessions under 3 hours
# spss_tutor_idx = df_with_prices[df_with_prices['post_text'].str.contains('datameer', case=False)==True].index

# try:
#     df_with_prices.iloc[spss_tutor_idx, price_col_idx] = 50
    
# except:
#     print("Issue with spss_tutor_idx and iloc.")
#     pass

# %%
# # Charges $50 per hour
# tutor_sam_idx = df_with_prices[df_with_prices['post_text'].str.contains('thetutorsam')==True].index

# try:
#     df_with_prices.iloc[tutor_sam_idx, price_col_idx] = 50
    
# except:
#     print("Issue with tutor_sam_idx and iloc.")
#     pass

# %%
# # Charges $40 per hour
# peter_d_idx = df_with_prices[df_with_prices['post_text'].str.contains('Peter D.')==True].index

# try:
#     df_with_prices.iloc[peter_d_idx, price_col_idx] = 40
# except:
#     print("Issue with peter_d_idx and iloc.")
#     pass    

# %%
# # Charges $45 per hour for individual lessons
# algebra_exclusively_idx = df_with_prices[df_with_prices['post_text'].str.contains('algebra EXCLUSIVELY')==True].index

# try:
#     df_with_prices.iloc[algebra_exclusively_idx, price_col_idx] = 45
# except:
#     print("Issue with algebra_exclusively_idx and iloc.")
#     pass    

# %%
# # Post includes many prices, but states $55/hr for Precalc and $80/hr for Calculus, which are primarily what I help with, so I took the average of those prices
# aerospace_engineer_idx = df_with_prices[df_with_prices['post_text'].str.contains('in the aerospace industry looking', regex=False)==True].index

# try:
#     df_with_prices.iloc[aerospace_engineer_idx, price_col_idx] = (55 + 80)/2

# except:
#     print("Issue with aerospace_engineer_idx and iloc.")
#     pass    

# %%
# # This ad mentions $45 for lower division college courses, which are a large segment of the subjects I help with, so I'm using that price to compare myself against.
# ucb_phd_student_and_ta_idx = df_with_prices[df_with_prices['post_text'].str.contains('Former UC-Berkeley economics Ph.D. student and TA')].index

# try:
#     df_with_prices.iloc[ucb_phd_student_and_ta_idx, price_col_idx] = 45

# except:
#     print("Issue with ucb_phd_student_and_ta_idx and iloc.")
#     pass

# %%
# # The add says $55/hr for K-12, then $65/hr for AP/Honors, as well as Pre-calc, 
# # etc., I'm going to average the two prices.
# park_academy_idx = df_with_prices[df_with_prices['post_text'].str.contains('(949) 490-0872', regex=False)==True].index

# try:
#     df_with_prices.iloc[park_academy_idx, price_col_idx] = 60

# except:
#     print("Issue with park_academy_idx and iloc.")
#     pass

# %%
# # Says $25/hr for high school, $30/hr for college, just went with $30/hr
# sharp_mind_idx = df_with_prices[df_with_prices['post_text'].str.contains('(650) 398-9490', regex=False)==True].index

# try:
#     df_with_prices.iloc[sharp_mind_idx, price_col_idx] = 30
    
# except:
#     print("Issue with sharp_mind_idx and iloc.")
#     pass

# %%
# # Says $50/hr if travelling, $30-35/hr if virtual, so I took the average of 50 and 35
# stock_tutor_idx = df_with_prices[df_with_prices['post_text'].str.contains('714.425.3828', regex=False)==True].index

# try:
#     df_with_prices.iloc[stock_tutor_idx, price_col_idx] = (35 + 50)/2
    
# except:
#     print("Issue with stock_tutor_idx and iloc.")
#     pass

# %%
# # Post says $30/hr for Precalc/Trig and $50/hr for Calculus, so I took the average
# lonzo_tutoring_idx = df_with_prices[df_with_prices['post_text'].str.contains('951-795-5027', regex=False)==True].index

# try:
#     df_with_prices.iloc[lonzo_tutoring_idx, price_col_idx] = 40

# except:
#     print("Issue with lonzo_tutoring_idx and iloc.")
#     pass    

# %%
# # This ad says $30 for one hour.
# poway_tutor_idx = df_with_prices[df_with_prices['post_text'].str.contains('(619)735-2579', regex=False)==True].index

# try:
#     df_with_prices.iloc[poway_tutor_idx, price_col_idx] = 30
    
# except:
#     print("Issue with poway_tutor_idx and iloc.")
#     pass

# %%
# # $20/hr online, $30/hr in person, split the difference at $25
# austin_sabrina_idx = df_with_prices[df_with_prices['post_text'].str.contains('My girlfriend Sabrina')==True].index

# try:
#     df_with_prices.iloc[austin_sabrina_idx, price_col_idx] = 25
    
# except:
#     print("Issue with austin_sabrina_idx and iloc.")
#     pass    

# %%
# # Says $25/hr
# alex_farrell_idx = df_with_prices[df_with_prices['post_text'].str.contains('Alexander Farrell')==True].index

# try:
#     df_with_prices.iloc[alex_farrell_idx, price_col_idx] = 25
# # 
# except:
#     print("Issue with alex_farrell_idx and iloc.")
#     pass    

# %%
# # $25/hr if meeting near CSU Sac, $35/hr if they drive to you, $20/hr for online.
# # I chose $30/hr to split the difference between the in person prices.
# best_math_idx = df_with_prices[df_with_prices['post_text'].str.contains('bestmathtutoring.com')==True].index

# try:
#     df_with_prices.iloc[best_math_idx, price_col_idx] = 30
    
# except:
#     print("Issue with best_math_idx and iloc.")
#     pass  

# %%
# ucla_grad_henry_idx = df_with_prices[df_with_prices['post_text'].str.contains("916 390-7923", regex=False)==True].index

# try:
#     df_with_prices.iloc[ucla_grad_henry_idx, price_col_idx] = 35

# except:
#     print("Issue with ucla_grad_henry_idx and iloc.")
#     pass    

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
# #### Ads where averaging doesn't make sense

# %%
# # This guy's ad says 35$/half hour, but explicitly says $57 per hour, so averaging doesn't make sense.  
# blake_tutoring_idx = df_with_prices[df_with_prices['post_text'].str.contains('BlakeTutoring.com', case=False)==True].index

# df_with_prices.iloc[blake_tutoring_idx, price_col_idx] = 57

# %%
# # This ad says $84/hr but then mentions a $125 for 1.5 hours.  Since these are the only two prices in the post, our code averages them, so we set the correct price to $84
# test_trainer_inc_idx = df_with_prices[df_with_prices['post_text'].str.contains("TestTrainerinc", regex=False)==True].index

# try:
#     df_with_prices.iloc[test_trainer_inc_idx, price_col_idx] = 84

# except:
#     print("Issue with test_trainer_inc_idx and iloc.")
#     pass 

# %%
# # This guy's ad says $60/45mins, but $80 per hour.  Either price comes out to the same hourly rate, so averaging doesn't make sense.
# hiro_kobayashi_idx = df_with_prices[df_with_prices['post_text'].str.contains('415-250-4831', case=False)==True].index

# df_with_prices.iloc[hiro_kobayashi_idx, price_col_idx] = 80

# %%
# # This guy's ad says $40/1hr, $70/2hr, so averaging doesn't make sense
# guy_with_suit_idx = df_with_prices[df_with_prices['post_text'].str.contains('trained mathematician with about 20 years experience')==True].index

# df_with_prices.iloc[guy_with_suit_idx, price_col_idx] = 40

# %%
# # This guy's ad says $25/1hr, $40/2hr, so averaging doesn't make sense
# christian_cerritos_college_idx = df_with_prices[df_with_prices['post_text'].str.contains('trained mathematician with about 20 years experience')==True].index

# df_with_prices.iloc[christian_cerritos_college_idx, price_col_idx] = 25

# %%
# # This guy's ad says $30/half hr, $50/1hr, so averaging doesn't make sense
# dustin_csu_long_beach_idx = df_with_prices[df_with_prices['post_text'].str.contains('International Society of Automation')==True].index

# df_with_prices.iloc[dustin_csu_long_beach_idx, price_col_idx] = 50

# %%
# # This guy's ad says $65/hr for subject tutoring, $100/hr for standardized tests.  I'm primarily competing against subject tutoring, so I'll use that price
# smarter_than_you_think_idx = df_with_prices[df_with_prices['post_text'].str.contains('guarantee you are smarter than you think')==True].index

# df_with_prices.iloc[smarter_than_you_think_idx, price_col_idx] = 65

# %%
# # This guy's ad says $50/hr or $160/4hr, so it doesn't make sense to average.
# dead_in_ditch_idx = df_with_prices[df_with_prices['post_text'].str.contains('dead in a ditch')==True].index

# df_with_prices.iloc[dead_in_ditch_idx, price_col_idx] = 50

# %%
# # This guy's ad says $45/hr +$10 more per student, so it doesn't make sense to average.
# distinguished_teacher_idx = df_with_prices[df_with_prices['post_text'].str.contains('"Distinguished Teacher"')==True].index

# df_with_prices.iloc[distinguished_teacher_idx, price_col_idx] = 45

# %%
# # This guy's ad says $40/hr +$10 more for each additional person, so it doesn't make sense to average.
# vahab_idx = df_with_prices[df_with_prices['post_text'].str.contains('vababtaghizade@gmail.com')==True].index

# df_with_prices.iloc[vahab_idx, price_col_idx] = 40

# %%
# # This guy's ad says $30/hr for trial session, then $60/hr afterwards, so it doesn't make sense to average.
# myles_ahead_idx = df_with_prices[df_with_prices['post_text'].str.contains('mylesaheadtutoring')==True].index

# df_with_prices.iloc[myles_ahead_idx, price_col_idx] = 60

# %%
# # This guy's ad says $45/hr, then talks about selling a workbook for $30, so it doesn't make sense to average.
# john_the_tutor_idx = df_with_prices[df_with_prices['post_text'].str.contains('480-343-2212')==True].index

# df_with_prices.iloc[john_the_tutor_idx, price_col_idx] = 45

# %%
df_with_prices = clean_two_prices(df_with_prices)

# %% [markdown]
# Conclusion: Averaging doesn't make sense for a good chunk of these posts, but averaging is helpful for others.  I need to come up with a better process here, but will leave that for later...

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
