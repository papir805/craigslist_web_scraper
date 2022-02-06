def get_state_to_region_dict(st_tags, rg_tags):
    """
    Input: 
        st_tags - State Tags: A list of HTML tags containing the names of US states on Craigslist
        rg_tags - Region Tags: A list of HTML tags containing the names of different regions in each state
        
    Output:
        st_dict - State Dict: A dict that maps state_name (str) to region_list (list), which contains regions on Craigslist for that state.
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



