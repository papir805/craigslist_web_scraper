def get_state_and_region_tags():
    import requests
    from requests.packages.urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    from bs4 import BeautifulSoup
    
    # Create a Session and Retry object to manage the quota Craigslist imposes on HTTP get requests within a certain time period 
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Parse URL that contains all regions of Craigslist
    all_sites_response = session.get('https://craigslist.org/about/sites')
    all_sites_soup = BeautifulSoup(all_sites_response.text, 'html.parser')

    # Extract part of webpage corresponding to regions in the US
    us_sites = all_sites_soup.body.section.div.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling

    # Extract HTML tags corresponding to the state name and region
    states_tags = us_sites.find_all('h4')
    regions_tags = us_sites.find_all('ul')
    
    return states_tags, regions_tags
    

def get_state_to_region_dict(state_tags, region_tags):
    """
    Input: 
        state_tags - A list of HTML tags containing the names of US states on Craigslist
        region_tags - A list of lists of HTML tags which contain the names of different regions in each state
        
    Output:
        state_to_region_dict: A dictionary that maps state_name (str) -> region_list (list), which contains all Craigslist regions corresponding to that state.
        
    Process: Use BeautifulSoup to extract state and region text from HTML tags pulled off Craigslist.  Create a dictionary that will give us a mapping between state_name (key) and the regions (values) Craigslist has listed in that state.
    """
    
    from bs4 import BeautifulSoup
    
    states_and_regions = list(zip(state_tags, region_tags))
    
    state_to_region_dict = {}
    
    # For each of the HTML tags, we get the text of which state the region belonged to and the text of the region's name.  We now have a dictionary with keys as states that map to a list of regions in that state
    for ele in states_and_regions:
        state_name = ele[0].text
        href_list = ele[1].find_all('li')
        temp_region_list = []
        for href in href_list:
            region_name = href.a['href'].replace('https://','').replace('.craigslist.org/','')
            temp_region_list.append(region_name)
            state_to_region_dict[state_name]=temp_region_list
            
    return state_to_region_dict



def get_region_search_page_urls(state_region_dict):
    """
    Input:
        state_region_dict - Dictionary that maps state names (keys) -> list of regions in that state(values)
    
    Output:
        search_page_url_dict - Dictionary that maps keys that are tuples (state, region) to values that are lists of URLs of Craigslist search pages corresponding to math tutor in that state/region
    
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
    
    search_page_url_dict = {}
    
    # Walk through each state in our st_reg_dict to get the HTML page corresponding to a search for "math tutor" in the services section
    for state in tqdm_notebook(state_region_dict.keys(), desc='Total Progress'): 
        num_state_regions = len(state_region_dict[state])
        for region in tqdm_notebook(state_region_dict[state], desc=F"Currently extracting URLs for {num_state_regions} regions in {state}", leave=False):
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
            search_page_url_dict[(state, region)] = region_response_list
            
    t_end = time.time()
    t_diff = t_end - t_start
    print(F"URLs of search pages finished extracting at {time.ctime()}")
    print(F"Total process time: {t_diff}")
            
    return search_page_url_dict




def get_urls_of_posts(search_pages):
    """
    Input:
        search_pages - Dict: A Dictionary with key: (state, region) that maps to a list of search URLs containing postings for that state/region on Craigslist
    
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



def process_and_get_urls(state_region_dict):
    """
    Wrapper function for get_region_search_page_urls() and get_urls_of_posts()
    
    Input:
        state_region_dict - Dictionary with keys that are state names and values that are a list of regions in that state
    
    Output:
        urls_of_posts - Dict: A dictionary with key: (state, region) that maps to a list of URLs for individual postings in that state/region
    
    Process: get_region_search_page_urls() extracts the URLs of search pages, then feeds those URLs into get_urls_of_posts(), which extracts the URLs of the individual postings themselves.
    """
    search_pg_urls = get_region_search_page_urls(state_region_dict)
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
        for post in tqdm_notebook(urls_dict[key], desc=F"Creating Soup Objects for each posting in {state}: {region}", leave=False, position=1):

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