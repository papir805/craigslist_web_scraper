def get_state_to_region_dict(st_tags, rg_tags):
    """
    Input: 
        st_tags - State Tags: A list of HTML tags containing the names of US states on Craigslist
        rg_tags - Region Tags: A list of HTML tags containing the names of different regions in each state
        
    Output:
        st_dict - State Dict: A dict that maps state_name (str) to region_list (list), which contains regions on Craigslist for that state.
        
    Extracts state and region text from HTML tags pulled off Craigslist that will give us a mapping between the name of a state and the regions Craigslist has in that state.
    """
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



def get_region_search_pg_urls(st_rg_dict, html_session):
    """
    Input:
        st_rg_dict - Dictionary with key: state that maps to a list of regions in that state
    Output:
        search_pg_url_dict - Dictionary with key: (state, region) that maps to list of URLs for each posting corresponding to math tutor in that state/region
    
    Get the URL that corresponds to a search of the services section for "math tutor."  Craigslist is limited to showing 120 results per page, so if a region has more than 120 postings, we extract URLs corresponding to the next page of results, until there is no next button anymore and we've extracted all URLs for that region.
    """
    
    import random
    import time
    from bs4 import BeautifulSoup
    from tqdm.notebook import tqdm
    # Walk through each state in our st_reg_dict to get the HTML page corresponding to a search for "math tutor" in the services section
    
    t_start = time.ctime()
    print(F"Process started at {t_start}")
    
    
    search_pg_url_dict = {}
    
    for state in tqdm(st_rg_dict.keys(), desc='Extracting URLs of all search pages'):        
        for region in tqdm(st_rg_dict[state], desc=F"Currently extracting URLs for {state}", leave=False):
            # This gets the first page of search results
            i=1

            current_response = html_session.get('https://' + region + '.craigslist.org/d/services/search/bbb?query=math%20tutor&sort=rel')

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
        # 3) No next button:
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
                            current_response = html_session.get(new_button)
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
            
    t_end = time.ctime()
    t_diff = t_end - t_start
    print(F"URLs of search pages finished extracting at {t_end}")
    print(F"Total process time: {t_diff}")
            
    return search_pg_url_dict