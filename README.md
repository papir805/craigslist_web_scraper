# CL_tutoring_scraper - ETL Web Scraper
## Goal: To build a dataset of tutoring prices that can be used to understand my competition as a math tutor
As a math tutor, with a majority of my business coming from word-of-mouth recommendations or Craigslist, I wanted to understand my competition.  I built this Craigslist web scraper, using Python, to grab prices of tutors from the services section, then stored the information in a PostgreSQL database, to be used later in exploratory data analysis (EDA).  Because I tutor math in addition to teaching, I'm curious to know how my prices compare to other tutors in my neighboring areas, as well as in other parts of the country.

Important Python libraries used: `Requests`, `BeautifulSoup`, `Pandas`, `NumPy`, `Psycopg2`, and `Sklearn`, among others.

## Method:

1. *Extract* posting information from Craigslist using `Requests` and `BeautifulSoup`
2. *Transform* data to my own specifications using `Pandas`, `NumPy`, and `Sklearn`
3. *Load* data into PostgreSQL database using `Psycopg2`

### To-Do List:
- [ ] Capture prices containing decimals using regular expressions
- [ ] Improve countdown timer during extraction process
- [ ] Modularize extraction process by breaking code into smaller chunks
  - [ ] Incorporate unit tests
- [X] input `Null` when a price is not able to be found from a post **(completed 1/7/22)**
- [X] Identify and remove duplicate posts **(completed 1/8/22)**
  - [ ] UPDATE: Some tutors have duplicate posts in other regions of the country, but change prices.  I need to discover some way of keeping these duplicates to better reflect changes in price among regional markets.
- [ ] Improve extraction process
  - [ ] When two prices are given
  - [ ] When three or more prices are given
  - [ ] When a post has an online price schedule vs. an in-person price schedule
- [X] Extract from top 10 regions in US **(completed 1/1/22)**
- [ ] Extract from *all* regions on https://www.craigslist.org/about/sites
  - [ ] Keep track of which state a given post was from
- [ ] Scrape price from post title
