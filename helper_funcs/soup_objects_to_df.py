def extract_post_features(soup_objects_dict, include_errors=False):
    """
    Input:
        soup_objects_dict - A dictionary with key: (state, region) that maps to a list of soup_objects, where each soup_object contains the HTML for a Craigslist posting.
    Output:
        concat_df - DataFrame: Pandas DataFrame object containing information that has been scraped from a soup_object.
        error_list_text - list: List of soup_objects where scraping the text from the post failed
        link_error_list - list: List of soup_objects where a link for the post couldn't be found
    Process:
        Walk through each search_region, walk through each soup_object in that region, and extract relevant information.  When scraping the text or the link of a post fails, add the soup_object for that post to an error list to inspect later.  Once all posts for a region have been scraped, they're turned into a Pandas DataFrame and added to df_list.  Once all regions have been scraped, all DataFrames in df_list are concatenated together.
    """
    
    import pandas as pd
    import numpy as np
    from bs4 import BeautifulSoup
    import re
    import datetime as dt
    
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
    
    # Get date of html request to label our output with.
    date_of_html_request = str(dt.date.today())
    # Include the date posts were scraped on to track tutoring prices over time.
    concat_df['posts_scraped_on'] = date_of_html_request
    
    concat_df_shape = concat_df.shape
    print(F"df shape: {concat_df_shape}")
    
    if include_errors == True:
        num_errors_with_text = len(error_list_text)
        num_errors_get_links = len(link_error_list)
        print(F"There were {num_errors_get_links} errors getting links and {num_errors_with_text} getting text")
        return concat_df, error_list_text, link_error_list
    else:
        return concat_df