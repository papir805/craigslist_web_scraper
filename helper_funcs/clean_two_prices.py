def clean_two_prices(df):
    
    price_col_idx = df.columns.get_loc('price')
    
    # This guy's ad says 35$/half hour, but explicitly says $57 per hour, so averaging doesn't make sense.  
    blake_tutoring_idx = df[df['post_text'].str.contains('BlakeTutoring.com', case=False)==True].index

    df.iloc[blake_tutoring_idx, price_col_idx] = 57
    
    # This ad says $84/hr but then mentions a $125 for 1.5 hours.  Since these are the only two prices in the post, our code averages them, so we set the correct price to $84
    test_trainer_inc_idx = df[df['post_text'].str.contains("TestTrainerinc", regex=False)==True].index

    try:
        df.iloc[test_trainer_inc_idx, price_col_idx] = 84

    except:
        print("Issue with test_trainer_inc_idx and iloc.")
        pass 
    
        # This guy's ad says $60/45mins, but $80 per hour.  Either price comes out to the same hourly rate, so averaging doesn't make sense.
    hiro_kobayashi_idx = df[df['post_text'].str.contains('415-250-4831', case=False)==True].index

    df.iloc[hiro_kobayashi_idx, price_col_idx] = 80
    
    # This guy's ad says $40/1hr, $70/2hr, so averaging doesn't make sense
    guy_with_suit_idx = df[df['post_text'].str.contains('trained mathematician with about 20 years experience')==True].index

    df.iloc[guy_with_suit_idx, price_col_idx] = 40
    
    
        # This guy's ad says $25/1hr, $40/2hr, so averaging doesn't make sense
    christian_cerritos_college_idx = df[df['post_text'].str.contains('trained mathematician with about 20 years experience')==True].index

    df.iloc[christian_cerritos_college_idx, price_col_idx] = 25
    
    # This guy's ad says $30/half hr, $50/1hr, so averaging doesn't make sense
    dustin_csu_long_beach_idx = df[df['post_text'].str.contains('International Society of Automation')==True].index

    df.iloc[dustin_csu_long_beach_idx, price_col_idx] = 50
    
        # This guy's ad says $65/hr for subject tutoring, $100/hr for standardized tests.  I'm primarily competing against subject tutoring, so I'll use that price
    smarter_than_you_think_idx = df[df['post_text'].str.contains('guarantee you are smarter than you think')==True].index

    df.iloc[smarter_than_you_think_idx, price_col_idx] = 65
    
        # This guy's ad says $50/hr or $160/4hr, so it doesn't make sense to average.
    dead_in_ditch_idx = df[df['post_text'].str.contains('dead in a ditch')==True].index

    df.iloc[dead_in_ditch_idx, price_col_idx] = 50
    
    # This guy's ad says $45/hr +$10 more per student, so it doesn't make sense to average.
    distinguished_teacher_idx = df[df['post_text'].str.contains('"Distinguished Teacher"')==True].index

    df.iloc[distinguished_teacher_idx, price_col_idx] = 45
    
        # This guy's ad says $40/hr +$10 more for each additional person, so it doesn't make sense to average.
    vahab_idx = df[df['post_text'].str.contains('vababtaghizade@gmail.com')==True].index

    df.iloc[vahab_idx, price_col_idx] = 40
    
        # This guy's ad says $30/hr for trial session, then $60/hr afterwards, so it doesn't make sense to average.
    myles_ahead_idx = df[df['post_text'].str.contains('mylesaheadtutoring')==True].index

    df.iloc[myles_ahead_idx, price_col_idx] = 60
    
        # This guy's ad says $45/hr, then talks about selling a workbook for $30, so it doesn't make sense to average.
    john_the_tutor_idx = df[df['post_text'].str.contains('480-343-2212')==True].index

    df.iloc[john_the_tutor_idx, price_col_idx] = 45
    
    return df