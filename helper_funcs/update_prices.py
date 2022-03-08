import pandas as pd

def update_prices(df: pd.DataFrame) -> pd.DataFrame:
    
    price_col_idx = df.columns.get_loc('price')
    
    
    # This ad says $50/hr but then mentions a prepay plan for $160 for 4 hours.  Since these are the only two prices in the post, our code averages them, so we set the correct price to $50
    google_maps_idx = df[df['post_text'].str.contains("willing to travel if Google Maps", regex=False)==True].index

    try:
        df.iloc[google_maps_idx, price_col_idx] = 50

    except:
        print("Issue with google_maps_idx and iloc.") 

    # This ad says $45/hr for high school or college, but then mentions a $35 for middle school.  Since these are the only two prices in the post, our code averages them, so we set the correct price to $45, since I primarily tutor high school or college students.
    rancho_penasquitos_idx = df[df['post_text'].str.contains("Rancho Penasquitos (Park Village Neighborhood)", regex=False)==True].index

    try:
        df.iloc[rancho_penasquitos_idx, price_col_idx] = 45

    except:
        print("Issue with rancho_penasquitos_idx and iloc.") 
    
    return df