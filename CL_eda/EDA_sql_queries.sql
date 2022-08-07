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

SELECT * FROM us_census_regions LIMIT 1;


-- Count of posts and mean price by US Census region for plotly express graph
WITH cl_tutoring_2022_02_03 AS (
    SELECT *
    FROM cl_tutoring
    WHERE date_scraped = '2022-02-03'
      AND price IS NOT NULL
      ),

cl_tutoring_w_census AS (
   SELECT cr.state
        , cr.state_code
        , cr.us_region 
        , COALESCE(cl.price, 0) AS price -- Should I be using COALESCE here?
                                         -- Should a state with no prices have 
                                         -- mean_price of 0 when we AVG in the 
                                         -- next block of the query?
        , cl.id
     FROM us_census_regions AS cr
LEFT JOIN cl_tutoring_2022_02_03 AS cl
       ON cr.state = cl.state
  ),

mean_price_size_by_us_region as (SELECT state
     , state_code
     , us_region
     , AVG(price) OVER (PARTITION BY us_region) AS mean_price
     , COUNT(id) OVER (PARTITION BY us_region) AS num_posts
     , ROW_NUMBER() OVER (PARTITION BY us_region, state) AS rn
 FROM cl_tutoring_w_census)

SELECT *
FROM mean_price_size_by_us_region
WHERE rn = 1
ORDER BY 1;


-- Count of posts and mean price by state for plotly express graph
WITH mean_price_size_by_state AS (
   SELECT cl.state
        , AVG(cl.price) AS mean_price
        , COUNT(cl.id) AS num_posts
     FROM cl_tutoring AS cl
    WHERE cl.date_scraped = '2022-02-03'
      AND cl.price IS NOT NULL
 GROUP BY cl.state
)

   SELECT cr.state
        , cr.state_code
        , COALESCE(mp.mean_price, 0) AS mean_price 
        , COALESCE(mp.num_posts, 0) AS num_posts 
     FROM us_census_regions AS cr
LEFT JOIN mean_price_size_by_state AS mp
       ON cr.state=mp.state
ORDER BY cr.state;


SELECT subregion
     , AVG(price) AS mean_price
     , COUNT(id) AS num_posts
FROM cl_tutoring
WHERE date_scraped = '2022-02-03'
  AND price IS NOT NULL
  AND region = 'sfbayarea'
GROUP BY subregion
ORDER BY 3 DESC;