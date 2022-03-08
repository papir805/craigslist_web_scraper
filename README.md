# CL_tutoring_scraper - ETL Web Scraper
## Goal: To build a dataset of tutoring prices that can be used to understand my competition as a math tutor
As a math tutor, with a majority of my business coming from word-of-mouth recommendations or Craigslist, I wanted to understand my competition.  I built this Craigslist web scraper, using Python, to grab prices of tutors from the services section, then stored the information in a PostgreSQL database, to be used later in exploratory data analysis (EDA).  Because I tutor math in addition to teaching, I'm curious to know how my prices compare to other tutors in my neighboring areas, as well as in other parts of the country.

Important Python libraries used: `Requests`, `BeautifulSoup`, `Pandas`, `NumPy`, `Psycopg2`, and `Sklearn`, among others.

![Extract, Transform, Load](https://github.com/papir805/craigslist_web_scraper/blob/master/etl._thumbnail.png)

## How to use this repository - 
If you're interested in seeing just the script and Python code that I wrote, [click here](https://github.com/papir805/craigslist_web_scraper/blob/master/v1.4craigslist_scraper_tutoring.py)

**Recommended: If you'd like to see what the Python script actually does, without running the script yourself, you can view the code *and* the outputs of that code by clicking [here](https://github.com/papir805/craigslist_web_scraper/blob/master/v1.4craigslist_scraper_tutoring.ipynb) or [here](https://nbviewer.org/github/papir805/craigslist_web_scraper/blob/master/v1.4craigslist_scraper_tutoring.ipynb).**


## Method:

1. *Extract* posting information from Craigslist using `Requests` and `BeautifulSoup`
2. *Transform* data to my own specifications using `Pandas`, `NumPy`, and `Sklearn`
3. *Load* data into PostgreSQL database using `Psycopg2`

# To-Do List:
- [ ] Make the search work for any regular expression in CL services section
- [ ] Capture prices containing decimals using regular expressions
- [X] Improve countdown timer during extraction process **(completed 1/9/22)**
- [ ] Modularize extraction process by breaking code into smaller chunks
- [ ] Modularize drop_posts_with_similar_text
    - [ ] Modularize extract_post_features()
  - [ ] Incorporate unit tests for each module
- [X] input `Null` when a price is not able to be found from a post **(completed 1/7/22)**
- [X] Identify and remove duplicate posts **(completed 1/8/22)**
  - [ ] UPDATE: Some tutors have duplicate posts in other regions of the country, but change prices.  I need to discover some way of keeping these duplicates to better reflect changes in price among regional markets.
- [ ] Improve extraction process for pricing information
  - [ ] When two prices are given, I currently average them, but I'd like to incorporate a better system
      - Idea: Consider only averaging when a range of prices is given (ie $30-40 per hour)
  - [ ] When three or more prices are given, I have to manually inspect each post and figure out how to distill to down a single price
  - [ ] When a post has an online price schedule vs. an in-person price schedule, I'd like to be able to keep track of the pricing difference
- [X] Extract from top 10 regions in US **(completed 1/1/22)**
- [X] Extract from *all* regions on https://www.craigslist.org/about/sites **(completed 1/26/22)**
  - [X] Keep track of which state a given post was from completed **(completed 1/26/22)**
  - [ ] Keep track of West, Central, or East coast
- [ ] Scrape price from post title
- [ ] Test limits of how quickly I can make HTML requests w/o a ban
- [X] Bypass search results when "Zero local results found.  Here are some from nearby areas." **(completed 1/26/22)**
