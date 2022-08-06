-- What is the mean hourly price for tutoring per state?
  SELECT cl.state
       , AVG(cl.price) AS mean_price
    FROM cl_tutoring AS cl
   WHERE cl.date_scraped = '2022-02-03' AND cl.price IS NOT NULL
GROUP BY cl.state
  HAVING COUNT(cl.id) >= 10
ORDER BY 2 DESC;

-- Which states had the most postings?
  SELECT cl.state
       , COUNT(cl.id) AS num_postings
    FROM cl_tutoring AS cl
   WHERE cl.date_scraped = '2022-02-03' AND cl.price IS NOT NULL
GROUP BY cl.state
  HAVING COUNT(cl.id) >= 10
ORDER BY 2 DESC;

-- Which state sub-regions had the most postings?
  SELECT cl.region
       , COUNT(cl.id) AS num_postings
    FROM cl_tutoring AS cl
   WHERE cl.date_scraped = '2022-02-03' AND cl.price IS NOT NULL
GROUP BY cl.region
  HAVING COUNT(cl.id) >= 10
ORDER BY 2 DESC;

-- What is the average hourly price by state sub-region?
  SELECT cl.region
       , AVG(cl.price) AS mean_price
    FROM cl_tutoring AS cl
   WHERE cl.date_scraped = '2022-02-03' AND cl.price IS NOT NULL
GROUP BY cl.region
  HAVING COUNT(cl.id) >= 10
ORDER BY 2 DESC;

-- What is the mean hourly price per state and number of 
-- postings for the ENTIRE dataset?
    WITH states_greater_10_posts AS (
  SELECT cl.state
    FROM cl_tutoring AS cl
   WHERE cl.date_scraped = '2022-02-03' AND cl.price IS NOT NULL
GROUP BY cl.state
  HAVING COUNT(cl.id) >= 10
)

  SELECT 'Other' AS state
       , AVG(price) AS mean_price
       , COUNT(*) AS num_posts
    FROM cl_tutoring
   WHERE state NOT IN (SELECT state 
                         FROM states_greater_10_posts)
     AND date_scraped = '2022-02-03' 
     AND price IS NOT NULL

   UNION 

  SELECT cl.state
       , AVG(cl.price) AS mean_price
       , COUNT(*) AS num_posts
    FROM cl_tutoring AS cl
   WHERE cl.date_scraped = '2022-02-03' AND cl.price IS NOT NULL
GROUP BY cl.state
  HAVING COUNT(cl.id) >= 10
ORDER BY 2 DESC;

-- What is the mean hourly price and number of postings by US Census Region?
WITH cl_tutoring_w_census AS (
   SELECT cl.*, cr.us_region, cr.us_division
     FROM cl_tutoring AS cl
LEFT JOIN us_census_regions AS cr
       ON cl.state = cr.state
    WHERE cl.date_scraped = '2022-02-03'
      AND cl.price IS NOT NULL
  )

   SELECT cltwc.us_region
        , AVG(cltwc.price) AS mean_price
        , COUNT(cltwc.id) AS num_postings
     FROM cl_tutoring_w_census AS cltwc
 GROUP BY cltwc.us_region;

-- What is the mean hourly price by US Census Division?
WITH cl_tutoring_w_census AS (
   SELECT cl.*, cr.us_region, cr.us_division
     FROM cl_tutoring AS cl
LEFT JOIN us_census_regions AS cr
       ON cl.state = cr.state
    WHERE cl.date_scraped = '2022-02-03'
      AND cl.price IS NOT NULL
  )

   SELECT cltwc.us_division
        , AVG(cltwc.price) AS mean_price
        , COUNT(cltwc.id) AS num_postings
     FROM cl_tutoring_w_census AS cltwc
 GROUP BY cltwc.us_division;

 SELECT * FROM cl_tutoring LIMIT 1;