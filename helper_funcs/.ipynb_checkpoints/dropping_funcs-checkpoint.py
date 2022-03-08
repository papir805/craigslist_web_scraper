import pandas as pd

def rows_before_and_after(df_before: pd.DataFrame, df_after: pd.DataFrame) -> None:
    """
        Input: 
            df_before: pandas DataFrame before dropping duplicate rows
            df_after: pandas DataFrame after dropping duplicate rows
            
        This function compares the difference in rows before and after dropping duplicate row.
    """
    num_rows_before = df_before.shape[0]
    num_rows_after = df_after.shape[0]
    num_rows_diff = abs(num_rows_before - num_rows_after)
    print(F"Number of rows before dropping duplicates: {num_rows_before}")
    print(F"Number of rows before after duplicates: {num_rows_after}")
    print(F"A difference of {num_rows_diff} rows.") 
    
    
def drop_exact_duplicates(input_df: pd.DataFrame, details: bool=True) -> pd.DataFrame:
    """
    Input:
        input_df - pandas DataFrame that has duplicated rows
        details - Boolean flag which if True, will print information regarding number of rows before and after dropping duplicate rows.
    
    Output:
        df_exact_text_dropped - pandas DataFrame after dropping duplicates rows
        
    Process: Get indices of rows that have identical post_text and drop all but the first instance of those duplicated rows.
    """
    
    import pandas as pd
    
    duplicate_indices = input_df[input_df['post_text'].duplicated(keep='first')==True].index
    df_exact_txt_dropped = input_df.drop(index=duplicate_indices)
    df_exact_txt_dropped = df_exact_txt_dropped.reset_index(drop=True)
    
    if details==True:
        rows_before_and_after(input_df, df_exact_txt_dropped)
    
    return df_exact_txt_dropped


def drop_posts_with_similar_text(input_df: pd.DataFrame, similarity_threshold: float = 0.63, drop_match_col: bool = True, details:bool = True) -> pd.DataFrame:
    """
    Input:
        intput_df - pandas DataFrame with rows that contain post_text which is similar to other rows in the DataFrame.  This is caused by people on Craigslist who post their ad in multiple regions, but change the text slightly to avoid getting flagged.
        similarity_threshold - A parameter which controls how similar the post_text should be before dropping it.  A similarity_threshold of 1 means the post_text is an exact copy of another post_text.  A post with a similarity_ratio >= similarity_threshold will be dropped.
        drop_match_col - Boolean which controls whether we drop the DataFrames match column.  This column is only needed to detect rows with similar post_text and is dropped by default as it is only really useful for debugging.  Set to True if you need to debug and verify the algorithm is dropping the correct rows.
        details - Boolean that prints details regarding number of rows before and after dropping similar post_text.
        
    Output:
        df_no_dups - pandas DataFrame which should contain listings that have post_text with a similarity ratio below the similarity threshold.  In theory, this means that each row should contain post_text that is unique, making the listing itself unique, and therefore the DataFrame contains no duplicates. 
    """
    
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    
        # Vectorize each posts' text and calculate the cosine similarity of each post against all other posts to determine which are duplicates
    ## https://kanoki.org/2018/12/27/text-matching-cosine-similarity/
    text_for_comparison = input_df['post_text']
    vect = TfidfVectorizer(min_df=1, stop_words='english')
    tfidf = vect.fit_transform(text_for_comparison)
    pairwise_similarity = tfidf * tfidf.T

    # Store results in a 2D NumPy array
    pairwise_array = pairwise_similarity.toarray()

    # The diagonal of our array is the similarity of a post to itself, which we fill will null so that these are essentially ignored
    np.fill_diagonal(pairwise_array, np.nan)

    # Many people on CL will change their posting in ways to avoid CL flagging them as duplicates for removal.  This finds all posts above a certain similarity threshold.
    argwhere_array = np.argwhere(pairwise_array > similarity_threshold)
    
    # In order to remove the duplicates, we need to restructure our 2D NumPy array in such a way that the first column is the index of the post that has a duplicate and the second column contains a list of the indices of the duplicate post(s).
    df_row_idx = []
    dup_row_idx = []
    for row in argwhere_array:
        current_idx = row[0]
        #print(F"Current row: {row}, Current idx: {current_idx}")
        duplicate_list = []
        if current_idx in df_row_idx:
            continue
        else:
            df_row_idx.append(current_idx)
        for other_row in argwhere_array:
            other_idx = other_row[1]
            #print(F"Here's the other_row: {other_row}, Other idx: {other_idx}")
            if current_idx == other_row[0]:
                duplicate_list.append(other_idx)
        #print(F"This is the current dup_list: {duplicate_list}")
        #print()
        dup_row_idx.append(duplicate_list)
    #list(zip(df_row_idx, dup_row_idx))
    
    # Create match column in our df, which is initialized as a list of all indices in our df.  This means for each row, the value of the match column is the row index.  Convert that index value to a list, so we can iterate over it in future steps
    input_df['match'] = np.array(input_df.index.values, dtype='object')
    input_df['match'] = input_df['match'].apply(lambda x: [x])

    # For rows that are duplicate postings, we overwrite the value of match column to contain the indices of all other rows that contain duplicated text
    match_col_idx = input_df.columns.get_loc('match')
    input_df.iloc[df_row_idx, match_col_idx] = np.array(dup_row_idx, dtype='object')
    #input_df['match'] = input_df['match'].apply(lambda x: [x])

    #input_df['match']
    
    indices = []

    df_no_dups = input_df.copy()

    # Iterate over each row and remove all rows that have duplicated text
    for i, row in df_no_dups.iterrows():
        indices.append(i)
        drop_idx = []
        #print(i, row['match'])
        try:
            for item in row['match']:
                if item not in indices:
                    drop_idx.append(item)
            df_no_dups = df_no_dups.drop(index=drop_idx, errors="ignore")
        except Exception as e:
            #print(i, item, row['match'])
            print(e, i, item, row['match'])
    
    if drop_match_col==True:
        input_df = input_df.drop('match', axis=1)
        df_no_dups = df_no_dups.drop('match', axis=1)
    
    if details==True:
        rows_before_and_after(input_df, df_no_dups)
    
    return df_no_dups


def drop_posts_without_prices(input_df: pd.DataFrame, details: bool = True) -> pd.DataFrame:
    """
    Input:
        input_df - pandas DataFrame where certain rows correspond to Craigslist postings that have no pricing information and will be dropped.
        details - Boolean which controls whether details regarding number of rows before and after rows have been dropped.
        
    Output:
        df_with_prices - pandas DataFrame where every row has pricing information.
    """
    # Use the len of price_list to find posts that contained no prices
    input_df['len_of_price_list'] = input_df['price_list'].apply(lambda x: len(x))

    # Filter out results that don't have a price and reset indices.
    df_with_prices = input_df[input_df['len_of_price_list'] > 0]
    df_with_prices = df_with_prices.reset_index(drop=True)
    
    if details==True:
        rows_before_and_after(input_df, df_with_prices)
    
    return df_with_prices


# def slim_df_down(input_df, drop_similar=True, drop_without_price=True, similarity_threshold=0.63):
#     """
    
#     """
    
#     df_post_text_dups_dropped = drop_exact_duplicates(input_df)
    
#     if drop_similar==True and drop_without_price = False:
#         df_post_text_dups_and_similar_dropped = drop_posts_with_similar_text(df_post_text_dups_dropped, similarity_threshold)
    
#     if drop_without_price==True:
#         df_no_dups_no_similar_that_have_price = drop_posts_without_prices(df_post_text_dups_and_similar_dropped)
