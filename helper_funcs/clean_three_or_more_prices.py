def clean_three_or_more_prices(df):
    price_col_idx = df.columns.get_loc('price')
    
    # Says $40 for in person, or $45 for at home, so I took the average.
    san_mateo_tutor_idx = df[df['post_text'].str.contains('I mainly tutor, in person, at the Downtown Redwood City, downtown San Mateo')].index

    try:
        df.iloc[san_mateo_tutor_idx,price_col_idx] = 42.5

    except:
        print("Issue with san_mateo_tutor and iloc.")
        
    
    # Because the ad says $90 in person, $60 for online, and Corona Virus pricing of
    # $40 for online weekdays, I'm using the $40 per hour rate because it seems the
    # most reasonable and is most similar to what I'm competing against.
    kenari_tutor_idx = df[df['post_text'].str.contains('kenaritutor.com')==True].index

    try:
        df.iloc[kenari_tutor_idx,price_col_idx] = 40
    except:
        print('Issue with kenari_tutor_idx and iloc.')
        

    # This ad mentions several prices for different subjects, but explicitly says $30 for math.
    la_honda_idx = df[df['post_text'].str.contains('909-640-3570')].index

    try:
        df.iloc[la_honda_idx,price_col_idx] = 30

    except:
        print("Issue with la_honda_idx and iloc.")
        
    
        # Says $60 per hour.
    glasses_lady_idx = df[df['post_text'].str.contains("offering virtual one-on-one Math tutoring via Zoom")==True].index

    try:
        df.iloc[glasses_lady_idx, price_col_idx] = 60
    except:
        print("Issue with glasses_lady_idx and iloc.")
          

    # Says #60 per hour.
    UC_Davis_data_scientist = df[df['post_text'].str.contains("PhD in Engineering from UC Davis")==True].index

    try:
        df.iloc[UC_Davis_data_scientist, price_col_idx] = 60
    except:
        print("Issue with UC_Davis_data_scientist and iloc.")
          
    
        #This guy has weird price structuring, but I used his hourly rate for each time interval, $100 for 80 minutes, $115 for 100 minutes, $130 for 120 minutes, then averaged those hourly rates to estimate what a single hour would cost.
    oakland_exp_tutor_online_idx = df[df['post_text'].str.contains('I received a full scholarship to University of Cincinnati and held a 3.8 GPA through my master’s program in aerospace')==True].index

    oakland_tutor_avg_rate = ((100/80) + (115/100) + (130/120)) * 60 / 3

    try:
        df.iloc[oakland_exp_tutor_online_idx, price_col_idx] = oakland_tutor_avg_rate

    except:
        print("Issue with oakland_exp_tutor_online_idx and iloc.")
        

        # The ad repeats the price of $40 over and over, so I'm replacing the price with 
    # a single instance.
    star_star_college_math_tutor_idx = df[df['post_text'].str.contains('https://www.youtube.com/channel/UCqhFZRmUqOAAPMQpo58TV7g'
                       ) == True].index

    try:
        df.iloc[star_star_college_math_tutor_idx, price_col_idx] = 40

    except:
        print("Issue with star_star_college_math_tutor_idx and iloc.")
        
    
    
    # Says $50/hr    
    trevor_skelly_idx = df[df['post_text'].str.contains('trevorskelly')==True].index

    try:
        df.iloc[trevor_skelly_idx,price_col_idx] = 50

    except:
        print("Issue with trevor_skelly_idx and iloc.")
        
    
    
        # Charges $50 per hour for sessions under 3 hours
    spss_tutor_idx = df[df['post_text'].str.contains('datameer', case=False)==True].index

    try:
        df.iloc[spss_tutor_idx, price_col_idx] = 50

    except:
        print("Issue with spss_tutor_idx and iloc.")
        
    
    
        # Charges $50 per hour
    tutor_sam_idx = df[df['post_text'].str.contains('thetutorsam')==True].index

    try:
        df.iloc[tutor_sam_idx, price_col_idx] = 50

    except:
        print("Issue with tutor_sam_idx and iloc.")
        
    
    # Charges $40 per hour
    peter_d_idx = df[df['post_text'].str.contains('Peter D.')==True].index

    try:
        df.iloc[peter_d_idx, price_col_idx] = 40
    except:
        print("Issue with peter_d_idx and iloc.")
            
    
    
        # Charges $45 per hour for individual lessons
    algebra_exclusively_idx = df[df['post_text'].str.contains('algebra EXCLUSIVELY')==True].index

    try:
        df.iloc[algebra_exclusively_idx, price_col_idx] = 45
    except:
        print("Issue with algebra_exclusively_idx and iloc.")
            
    
        # Post includes many prices, but states $55/hr for Precalc and $80/hr for Calculus, which are primarily what I help with, so I took the average of those prices
    aerospace_engineer_idx = df[df['post_text'].str.contains('in the aerospace industry looking', regex=False)==True].index

    try:
        df.iloc[aerospace_engineer_idx, price_col_idx] = (55 + 80)/2

    except:
        print("Issue with aerospace_engineer_idx and iloc.")
            
    
    
        # This ad mentions $45 for lower division college courses, which are a large segment of the subjects I help with, so I'm using that price to compare myself against.
    ucb_phd_student_and_ta_idx = df[df['post_text'].str.contains('Former UC-Berkeley economics Ph.D. student and TA')].index

    try:
        df.iloc[ucb_phd_student_and_ta_idx, price_col_idx] = 45

    except:
        print("Issue with ucb_phd_student_and_ta_idx and iloc.")
    

    # The add says $55/hr for K-12, then $65/hr for AP/Honors, as well as Pre-calc, 
    # etc., I'm going to average the two prices.
    park_academy_idx = df[df['post_text'].str.contains('(949) 490-0872', regex=False)==True].index

    try:
        df.iloc[park_academy_idx, price_col_idx] = 60

    except:
        print("Issue with park_academy_idx and iloc.")
        
    
        # Says $25/hr for high school, $30/hr for college, just went with $30/hr
    sharp_mind_idx = df[df['post_text'].str.contains('(650) 398-9490', regex=False)==True].index

    try:
        df.iloc[sharp_mind_idx, price_col_idx] = 30

    except:
        print("Issue with sharp_mind_idx and iloc.")
        
    
        # Says $50/hr if travelling, $30-35/hr if virtual, so I took the average of 50 and 35
    stock_tutor_idx = df[df['post_text'].str.contains('714.425.3828', regex=False)==True].index

    try:
        df.iloc[stock_tutor_idx, price_col_idx] = (35 + 50)/2

    except:
        print("Issue with stock_tutor_idx and iloc.")
        
    
        # Post says $30/hr for Precalc/Trig and $50/hr for Calculus, so I took the average
    lonzo_tutoring_idx = df[df['post_text'].str.contains('951-795-5027', regex=False)==True].index

    try:
        df.iloc[lonzo_tutoring_idx, price_col_idx] = 40

    except:
        print("Issue with lonzo_tutoring_idx and iloc.")
            
    
    
        # This ad says $30 for one hour.
    poway_tutor_idx = df[df['post_text'].str.contains('(619)735-2579', regex=False)==True].index

    try:
        df.iloc[poway_tutor_idx, price_col_idx] = 30

    except:
        print("Issue with poway_tutor_idx and iloc.")
        
    
    
        # $20/hr online, $30/hr in person, split the difference at $25
    austin_sabrina_idx = df[df['post_text'].str.contains('My girlfriend Sabrina')==True].index

    try:
        df.iloc[austin_sabrina_idx, price_col_idx] = 25

    except:
        print("Issue with austin_sabrina_idx and iloc.")
            
    

        # Says $25/hr
    alex_farrell_idx = df[df['post_text'].str.contains('Alexander Farrell')==True].index

    try:
        df.iloc[alex_farrell_idx, price_col_idx] = 25

    except:
        print("Issue with alex_farrell_idx and iloc.")
            
    

        # $25/hr if meeting near CSU Sac, $35/hr if they drive to you, $20/hr for online.
    # I chose $30/hr to split the difference between the in person prices.
    best_math_idx = df[df['post_text'].str.contains('bestmathtutoring.com')==True].index

    try:
        df.iloc[best_math_idx, price_col_idx] = 30

    except:
        print("Issue with best_math_idx and iloc.")
          
    
    
    ucla_grad_henry_idx = df[df['post_text'].str.contains("916 390-7923", regex=False)==True].index

    try:
        df.iloc[ucla_grad_henry_idx, price_col_idx] = 35

    except:
        print("Issue with ucla_grad_henry_idx and iloc.")
            
    
    
    return df