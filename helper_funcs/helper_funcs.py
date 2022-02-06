def get_state_to_region_dict(st_tags, rg_tags):
    """
    Input: 
        st_tags - State Tags: A list of HTML tags containing the names of US states on Craigslist
        rg_tags - Region Tags: A list of HTML tags containing the names of different regions in each state
        
    Output:
        st_dict - State Dict: A dict that maps state_name (str) to region_list (list), which contains regions on Craigslist for that state.
        
    Process: Use BeautifulSoup to extract state and region text from HTML tags pulled off Craigslist and create a dictionary that will give us a mapping between the name of a state (key) and the regions (values) Craigslist has listed in that state.
    """
    
    from bs4 import BeautifulSoup
    
    states_and_regions = list(zip(st_tags, rg_tags))
    
    st_to_rg_dict = {}
    
    # For each of the HTML tags, we get the text of which state the region belonged to and the text of the region's name.  We now have a dictionary with keys as states that map to a list of regions in that state
    for ele in states_and_regions:
        state_name = ele[0].text
        href_list = ele[1].find_all('li')
        temp_region_list = []
        for href in href_list:
            region_name = href.a['href'].replace('https://','').replace('.craigslist.org/','')
            temp_region_list.append(region_name)
            st_to_rg_dict[state_name]=temp_region_list
            
    return st_to_rg_dict



def get_region_search_pg_urls(st_rg_dict):
    """
    Input:
        st_rg_dict - Dictionary with keys that are state names and values that are a list of regions in that state
    
    Output:
        search_pg_url_dict - Dictionary with keys that are tuples (state, region) and values that are a list of URLs of Craigslist search pages corresponding to math tutor in that state/region
    
    Process: Use requests library to get the URL that corresponds to a search of the services section for "math tutor" for all state/region pairs.  Because Craigslist is limited to showing 120 results per search page, if a region has more than 120 postings, we extract URLs corresponding to the next page of results.  We do this until there is no next button anymore and we've extracted all search page URLs for that region.
    """
    
    import random
    import time
    import requests
    from requests.packages.urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    from bs4 import BeautifulSoup
    from tqdm.notebook import tqdm_notebook

    
    t_start = time.time()
    print(F"Process started at {time.ctime()}")
    
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    search_pg_url_dict = {}
    
    # Walk through each state in our st_reg_dict to get the HTML page corresponding to a search for "math tutor" in the services section
    for state in tqdm_notebook(st_rg_dict.keys(), desc='Total Progress'):     
        for region in tqdm_notebook(st_rg_dict[state], desc=F"Currently extracting URLs for {state}", leave=False):
            # This gets the first page of search results
            i=1

            current_response = session.get('https://' + region + '.craigslist.org/d/services/search/bbb?query=math%20tutor&sort=rel')

            sleep_timer = random.randint(2,4)
            time.sleep(sleep_timer)
            #print(F"Response #{i} for {state}: {region} received.")

            region_response_list = []
            region_response_list.append(current_response)

            # This gets all subsequent pages, using the next button from the search page
            is_next_button = True
            while is_next_button:
                try:
                    next_response = current_response
                    next_soup = BeautifulSoup(next_response.text, 'html.parser')

    # CL search pages have one of the following:
        # 1) A next button:
            # - when the region contains more than 120 posts for a given search
        # 2) A greyed out next button:
            # - when you've reached the last page of search results and there are no more
            # OR
            # - when a page has less than 120 results.
        # 3) No next button shown:
            # - when a page has less than 120 results
    # html suffix is None type when a next button isn't shown
    # html suffix is '' when the next button is greyed out.  This can happen in either case 2) or 3) from above
    # The while loop only needs to be peformed in case 1) when there is a next button you can click
                    html_suffix = next_soup.find(class_='button next')
                    #print(html_suffix)
                    if html_suffix is not None:
                        html_suffix = html_suffix.get('href')
                        #print("html_suffix is not none")
                        if html_suffix != '':
                            i += 1
                            #print(i, html_suffix)
                            #print('html_suffix is not blank')
                            new_button = 'https://' + region + '.craigslist.org' + html_suffix
                            current_response = session.get(new_button)
                            region_response_list.append(current_response)

                            sleep_timer = random.randint(2,4)
                            time.sleep(sleep_timer)
                            #print(F"{region} {i} response received.")
                            #print(F"Waiting {sleep_timer} seconds...")
                            #print()
                        else:
                            is_next_button = False
                            #print('html_suffix is blank')
                            #print(F"Last response for {region} received.  Process completed.")
                            #print()
                    else:
                        is_next_button = False
                        #print('next_button is None')
                        #print(F"Last response for {region} received.  Process completed.")
                        #print()
                        pass
                except:
                    is_next_button = False
                    pass

            # Store all search pages for math tutor
            search_pg_url_dict[(state, region)] = region_response_list
            
    t_end = time.time()
    t_diff = t_end - t_start
    print(F"URLs of search pages finished extracting at {time.ctime()}")
    print(F"Total process time: {t_diff}")
            
    return search_pg_url_dict




def get_urls_of_posts(search_pages):
    """
    Input:
        search_pages - Dict: A Dictionary with key: (state, region) that maps to a list of search URLs that contain postings for that state/region on Craigslist
    
    Output:
        urls_of_posts - Dict: A dictionary with key: (state, region) that maps to a list of URLs for all individual postings in that state/region
    
    Process: Walk through each state/region combo in search_pages and use BeautifulSoup to extract the URLs of each search result for a given state/region pair.
    """
    from bs4 import BeautifulSoup
    from tqdm.notebook import tqdm_notebook
    
    urls_of_posts = {}
    for key, responses in tqdm_notebook(search_pages.items(), desc="Extracting URLs"):
        state = key[0]
        region = key[1]
        #current_region = region
        region_posts = []
        for response in responses:
            current_html_soup = BeautifulSoup(response.text, 'html.parser')
            current_posts = current_html_soup.find_all('li', class_='result-row')
            wanted_posts = []
            for post in current_posts:
    # Many CL pages have "results from nearby areas", for instance some results for sandiego.craigslist.org show up in the losangeles.craigslist.org.  By comparing the region that we're currently scraping from against the URL of the posts, we can detect if it's from a nearby region or not.  To avoid duplicates and make the script finish more quickly, We only want to include posts where the URL of the post matches the region we're scraping from
                if post.a.get('href').replace('https://','').split('.')[0] == region:
                    wanted_posts.append(post)
            region_posts.extend(wanted_posts)
        urls_of_posts[(state,region)] = region_posts
        
    return urls_of_posts



def process_and_get_urls(st_rg_dict):
    """
    Wrapper function for get_region_search_pg_urls() and get_urls_of_posts()
    
    Input:
        st_rg_dict - Dictionary with keys that are state names and values that are a list of regions in that state
    
    Output:
        urls_of_posts - Dict: A dictionary with key: (state, region) that maps to a list of URLs for individual postings in that state/region
    
    Process: get_region_search_pg_urls() extracts the URLs of search pages, then feeds those URLs into get_urls_of_posts(), which extracts the URLs of the individual postings themselves.
    """
    search_pg_urls = get_region_search_pg_urls(st_rg_dict)
    urls_of_posts = get_urls_of_posts(search_pg_urls)
    
    return urls_of_posts



def convert_urls_to_soup_objs(urls_dict):
    """
    Input:
        urls_dict - Dict: A dictionary with key: (state, region) that maps to a list of URLs for individual postings in that state/region.
    Output:
        soup_objects_dict - Dict: A dictionary with key: (state, region) that maps to a list of soup_objects, where each soup_object contains the HTML for a Craigslist posting.
        
    Process: Convert each URL for a Craigslist posting to a BeautiflSoup soup_object.  Create dictionary with key (state, region) and values are soup_objects for a given state/region pair.
    """
    import datetime as dt
    import random
    import time
    import requests
    from requests.packages.urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    from bs4 import BeautifulSoup
    from tqdm.notebook import tqdm_notebook
    
    soup_objects_dict = {}
    
    num_posts = 0
    for state_and_region in urls_dict:
        num_posts += len(urls_dict[state_and_region])
    num_posts_remaining = num_posts
    
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # current_time = dt.datetime.now()
    # max_seconds_until_finish = num_posts * 4
    # max_finish_time = current_time + dt.timedelta(seconds=max_seconds_until_finish)

    #print(F"Current time is {current_time.strftime('%H:%M:%S')}")
    #print(F"Process estimated to finish before {max_finish_time.strftime('%H:%M:%S')}")
    #print()

    for key in tqdm_notebook(urls_dict, desc="Total Progress", position=0, leave=True):
        # Walk through each region and create a list of soup_objects to scrape from by storing them into memory.  This way we only have to send these get requests once and Craigslist doesn't ban us for sending the same https requests over and over
        soup_objects_list = []

        state = key[0]
        region = key[1]
        for post in tqdm_notebook(urls_dict[key], desc=F"Creating Soup Object for {state}: {region}", leave=False, position=1):

            # Impose a timer to help prevent from getting banned for too many HTTP requests in too short a time period.
            random_int = random.randint(2,4)
            time.sleep(random_int)
            current_link = post.a.get('href')
            response_object = session.get(current_link)
            soup_object = BeautifulSoup(response_object.text, 'html.parser')
            soup_objects_list.append(soup_object) 

            # Impose condition that every 10th post will trigger something printed to the screen.  This part of the code is a long process and I wanted something to help keep track of how much progress has been made
            #if (i !=0) and ((i-1) % 10 == 9):
                #print(F"Post number {i} in {key} is being extracted.")

        soup_objects_dict[key] = soup_objects_list
#         if count != len(urls_dict):
#             num_posts_remaining -= len(urls_dict[key])
#             current_time = dt.datetime.now()
#             new_seconds_until_finish = num_posts_remaining * 5
#             new_max_finish_time = current_time + dt.timedelta(seconds=new_seconds_until_finish)

#             state = key[0]
#             region = key[1]

            #print(F"Soup objects for {state}: {region} acquired.  Waiting for next region...")
            #print(F"Process will now finish by {new_max_finish_time.strftime('%H:%M:%S')}")
            #print()
        #else:
            #print()
            #print(F"Soup objects for {key} acquired.  Process complete.")

    return soup_objects_dict



def extract_post_features(soup_objects_dict, include_errors=False):
    """
    Input:
        soup_objects_dict - Dict:
    Output:
        concat_df - DataFrame:
        error_list_text - list:
        link_error_list - list:
    Process:
        asda
    """
    
    import pandas as pd
    import numpy as np
    from bs4 import BeautifulSoup
    import re
    
    df_list = []
    error_list_text = []
    link_error_list = []

    # Walk through lists of soup objects corresponding to an individual posting for a math tutor in a given search_region.
    for search_region in soup_objects_dict:
        # Initialize several lists to store relevant information for analysis
        price_list = []
        city_list = []
        datetime_list = []
        body_text_list = []
        subregion_list = []
        region_list = []
        link_list = []
        search_region_price_list = []
        state_list = []

        # Walk through each soup object in the list corresponding to the search region
        for soup in soup_objects_dict[search_region]:
            try:
                # Get link of post
                link = soup.find("meta", property="og:url")['content']
            except:
                # In case a link can't be found, we add the soup object to a list to inspect later and set link to 'None', which we'll use as a filter later so Python doesn't try to scrape from them.  Without a link, we don't want to scrape though, so we pass to the next iteration of the loop.
                link = 'None'
                link_error_list.append(soup)
                pass
                #print("Couldn't get link")

            try:
                # Extract region of post from Craigslist
                post_region = soup.find_all('li',class_='crumb area')[0].find('a').get_text()
                if post_region=='sf bay area':
                    post_region = 'sfbay'
                else:
                    post_region = post_region.replace(' ', '')
                post_region = post_region.lower()

            except:
                post_region = 'region not found'

            # Get text of postingbody of the post and remove unwanted text.
            try:
                text = soup.find('section', id='postingbody').get_text()
                text = text.replace(u'\xa0', u' ')
                # We do this so that we can use ; as a delimiter when copying data from a CSV file into a SQL database later.
                text = text.replace(';', ',') 
                # We do this because one post in particular had this text and was giving me trouble.  The best way I could find to handle it was to remove the text.
                text = text.replace('QR Code Link to This Post', '') 

            except:
                error_list_text.append(soup)
                text = 'text not found'
                #body_text_list.append(text)
                #print("Couldn't get text")

            state = search_region[0]
            state_list.append(state)
            region_list.append(post_region)
            link_list.append(link)
            body_text_list.append(text)

            # Use regular expressions to find all instances of prices in the text
            #old_prices = re.findall('(?:[\$]{1}[,\d]+.?\d*)', text)
            old_prices = re.findall('(?:[\$]{1}[,\d]+\d*)', text)
            # Alternative, if trying to capture decimals 
            # ^(?:\${1}\d+(?:,\d{3})*(?:\.{1}\d{2}){0,1})?$

            # Intialize empty list to store the new prices after processing old prices.
            new_prices = []
            #print(F"Initialized new_prices: {new_prices}")

            #Walk through each price in the post.
            for price in old_prices:
                # Clean unwanted characters.
                price = price.replace('$', '')
                price = price.replace('/', '')
                price = price.replace('!', '')
                price = price.replace('h', '')
                price = price.replace('.', '')
                price = price.replace(')', '')
                price = price.replace(',', '')
                price = price.replace('>', '')
                price = price.rstrip()   
                # Some tutors give prices as a range ie '$30-40'.  In order to work with this data, I split based on the hyphen, then I can use each price individually.
                split_prices = price.split('-')
            #print(F"Here are the old_prices: {old_prices}")
            #print(F"Here are the split_prices: {split_prices}")

                # Walk through the split price, if a price had no hypen, the split_prices has one price in it that we perform processing on.  If a hyphen was present, then we have multiple prices that we iterate over and process
                for p in split_prices:
                    # Only proceed if the post contained prices, ie if p is a non-empty string.
                    if len(p)!=0:
                        try:
                            # Convert string price to int.
                            new_int = int(p)
                            # Ignore prices which are too high to be reasonable.  Some posts included scholarship amounts as ways for a tutor to boast about their abilities, but this will only allow dollar amounts that are reasonable through.
                            if new_int <= 200:
                                new_prices.append(new_int)

                        except:
                            # Show which prices aren't able to convert to an int and the post they came from so we can isolate and fix the issue if need be.
                            print(F'Error converting this price: {p}')
                            print(split_prices)
                            print()
                            print('Here is the text of the post:')
                            print()
                            print(text)
                            print('-'*50)
                            print()
                            # Set prices that can't be covered to NaN so the process can finish.
                            new_prices.append(np.nan) 
            #print(F"Here are the processed new_prices: {new_prices}")
                    #print(len(new_prices))


            # Append all prices from the post to a separate list, in case we need to isolate issues and fix them later.

            search_region_price_list.append(new_prices)

            # For posts that had no prices listed, we use null
            if len(new_prices)==0:
                price_list.append(np.nan)
            # For posts that had a single price, we use it.
            elif len(new_prices)==1:
                price_list.append(new_prices[0])
            # For posts that contained two prices, we average them.  This isn't a perfect system but is mainly targeted to posts that give a range of prices (ie $25-30).
            elif len(new_prices)==2:
                avg_price_2 = np.average(new_prices)
                price_list.append(avg_price_2)
            # If a post has more than 3 prices, we append null.  We'll have to inspect these posts manually and deal with them later.
            else:
                price_list.append(np.nan)
            #print(price_list)


            # Get city information for each posting.
            try:
                city = soup.find(class_='postingtitletext').small.get_text()

                # Because of the way CL operates, one has to choose a city from a radio button list, that CL provides, when one creates a post to offer a service, however later, there's a field where they can type in any city they want.  Many people will randomly choose a city from the radio button list, but then  post their city as "online".  This makes sure we capture them. 
                re_pattern = re.compile('online')
                online_flag = re.search(re_pattern, city.lower())
                if online_flag:
                    city_list.append('Online')
                else:
                    # Strip out leading and trailing white spaces, replace parentheses, and capitalize each word in the str.
                    city = city.strip()
                    city = city.replace('(', '').replace(')', '')        
                    city = city.title()
                    city_list.append(city)
            except:
                # If a post has no city information, use None
                city_list.append('no city found')

            # Extract subregion of Craigslist that the post was made in. This will allow for comparison of prices across different cities within the same metropolitan sub_region.
            try:
                subregion = soup.find_all('li', class_='crumb subarea')[0].find('a').get_text()
                subregion = subregion.title()
                subregion_list.append(subregion)
            except:
                subregion_list.append('no subregion found')


            # Extract time the posting was made.
            try:
                dt_object = soup.find('time')['datetime']
                datetime_list.append(dt_object)
            except:
                datetime_list.append('time of post unavailable')
        # else:
        #     pass
        #print(price_list)
        # Create temporary df to store results for each region
        temp_df = pd.DataFrame(data=zip(datetime_list,
                                        link_list, 
                                        price_list, 
                                        city_list, 
                                        subregion_list, 
                                        region_list,
                                        state_list,
                                        body_text_list,
                                        search_region_price_list),
                            columns=['date_posted', 
                                     'link', 
                                     'price', 
                                     'city', 
                                     'subregion', 
                                     'region',
                                     'state',
                                     'post_text',
                                     'price_list']
                              )
        df_list.append(temp_df)
        
    # Concatenate the dfs for each region into one larger df and check its shape.
    concat_df = pd.concat(df_list, ignore_index=True)
    
    concat_df_shape = concat_df.shape
    print(F"df shape: {concat_df_shape}")
    
    if include_errors == True:
        num_errors_with_text = len(error_list_text)
        num_errors_get_links = len(link_error_list)
        print(F"There were {num_errors_get_links} errors getting links and {num_errors_with_text} getting text")
        return concat_df, error_list_text, link_error_list
    else:
        return concat_df