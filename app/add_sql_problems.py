#!/usr/bin/env python3
"""
Script to add SQL practice questions to the problems database
"""

import sqlite3
import json
from datetime import datetime

def add_sql_problems():
    conn = sqlite3.connect('interview_sessions.db')
    cursor = conn.cursor()
    
    # SQL Practice Questions - Medium Difficulty
    medium_sql_problems = [
        {
            "title": "Netflix - User's Fourth Favorite Movie",
            "description": """Write a query to find the fourth most-watched movie for each user. Output the user ID, movie title, and total watch time.
            
Assumptions:
- A user's most-watched movie is determined by total watch time
- If a user has watched fewer than 4 movies, exclude them from results""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["window-functions", "ranking", "netflix"],
            "examples": [
                {
                    "explanation": "Sample data shows users and their movie watch times. We need to rank movies by watch time per user and get the 4th ranked movie.",
                    "sample_tables": {
                        "user_viewing": {
                            "user_id": "int",
                            "movie_title": "varchar",
                            "watch_time_minutes": "int"
                        }
                    }
                }
            ],
            "solution": """WITH movie_ranking AS (
  SELECT 
    user_id,
    movie_title,
    watch_time_minutes,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY watch_time_minutes DESC) as rank
  FROM user_viewing
)

SELECT 
  user_id,
  movie_title,
  watch_time_minutes
FROM movie_ranking
WHERE rank = 4;""",
            "test_cases": [
                {
                    "input": "user_viewing table with sample data",
                    "expected_output": "Users with their 4th most watched movies"
                }
            ]
        },
        {
            "title": "PayPal - Transaction Success vs Failure Rate",
            "description": """Write a query to calculate the percentage breakdown of successful vs failed transactions for each payment method. Round percentages to 2 decimal places.

Notes:
- Calculate success rate as: Successful transactions / Total transactions * 100
- Calculate failure rate as: Failed transactions / Total transactions * 100""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["aggregation", "percentage", "paypal"],
            "examples": [
                {
                    "explanation": "Sample transaction data with status and payment methods. Calculate success/failure rates per payment method.",
                    "sample_tables": {
                        "transactions": {
                            "transaction_id": "int",
                            "payment_method": "varchar",
                            "status": "varchar",
                            "amount": "decimal"
                        }
                    }
                }
            ],
            "solution": """WITH payment_stats AS (
  SELECT 
    payment_method,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
  FROM transactions
  GROUP BY payment_method
)

SELECT 
  payment_method,
  ROUND((successful * 100.0 / total_transactions), 2) as success_rate,
  ROUND((failed * 100.0 / total_transactions), 2) as failure_rate
FROM payment_stats
ORDER BY success_rate DESC;""",
            "test_cases": []
        },
        {
            "title": "LinkedIn - Connection Growth Trend",
            "description": """Write a query to calculate the 7-day rolling average of new connections for each user. Output user ID, date, and rolling average rounded to 2 decimal places.

Notes:
- Rolling average should include current day and 6 preceding days
- Only include users who have made connections on at least 7 different days""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["window-functions", "rolling-average", "linkedin"],
            "examples": [
                {
                    "explanation": "Connection data showing when users made new connections. Calculate 7-day rolling average.",
                    "sample_tables": {
                        "connections": {
                            "user_id": "int",
                            "connection_date": "date",
                            "new_connections": "int"
                        }
                    }
                }
            ],
            "solution": """SELECT 
  user_id,
  connection_date,
  ROUND(AVG(new_connections) OVER (
    PARTITION BY user_id 
    ORDER BY connection_date 
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ), 2) as rolling_avg_7_days
FROM connections
WHERE user_id IN (
  SELECT user_id 
  FROM connections 
  GROUP BY user_id 
  HAVING COUNT(DISTINCT connection_date) >= 7
)
ORDER BY user_id, connection_date;""",
            "test_cases": []
        },
        {
            "title": "Airbnb - Top 2 Host Properties by Revenue",
            "description": """Write a query to find the top 2 highest revenue-generating properties for each host in 2023. Output host ID, property ID, and total revenue.

Assumptions:
- Revenue is calculated as sum of all booking amounts for the property
- If a host has fewer than 2 properties, show all their properties""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["ranking", "revenue", "airbnb"],
            "examples": [
                {
                    "explanation": "Booking data with property and host information. Find top 2 revenue properties per host.",
                    "sample_tables": {
                        "bookings": {
                            "host_id": "int",
                            "property_id": "int", 
                            "booking_amount": "decimal",
                            "booking_date": "date"
                        }
                    }
                }
            ],
            "solution": """WITH property_revenue AS (
  SELECT 
    host_id,
    property_id,
    SUM(booking_amount) as total_revenue
  FROM bookings
  WHERE EXTRACT(YEAR FROM booking_date) = 2023
  GROUP BY host_id, property_id
),

revenue_ranking AS (
  SELECT 
    host_id,
    property_id,
    total_revenue,
    ROW_NUMBER() OVER (PARTITION BY host_id ORDER BY total_revenue DESC) as revenue_rank
  FROM property_revenue
)

SELECT 
  host_id,
  property_id,
  total_revenue
FROM revenue_ranking
WHERE revenue_rank <= 2
ORDER BY host_id, revenue_rank;""",
            "test_cases": []
        },
        {
            "title": "Instagram - Engagement Rate Analysis",
            "description": """Write a query to calculate the engagement rate for each user's posts. Output user ID and engagement rate as a percentage rounded to 2 decimal places.

Definition:
- Engagement rate = (Likes + Comments) / Followers * 100
- Only include users with at least 1000 followers""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["engagement", "social-media", "instagram"],
            "examples": [
                {
                    "explanation": "User posts with likes/comments and user follower counts. Calculate engagement rates.",
                    "sample_tables": {
                        "posts": {
                            "user_id": "int",
                            "post_id": "int",
                            "likes": "int",
                            "comments": "int"
                        },
                        "users": {
                            "user_id": "int",
                            "followers": "int"
                        }
                    }
                }
            ],
            "solution": """WITH user_engagement AS (
  SELECT 
    p.user_id,
    SUM(p.likes + p.comments) as total_engagement,
    u.followers
  FROM posts p
  JOIN users u ON p.user_id = u.user_id
  WHERE u.followers >= 1000
  GROUP BY p.user_id, u.followers
)

SELECT 
  user_id,
  ROUND((total_engagement * 100.0 / followers), 2) as engagement_rate
FROM user_engagement
ORDER BY engagement_rate DESC;""",
            "test_cases": []
        },
        {
            "title": "Zoom - Meeting Duration Analysis",
            "description": """Write a query to find the average meeting duration for each day of the week. Output day name and average duration in minutes rounded to 1 decimal place.

Notes:
- Only include meetings that actually started (not scheduled but unused)
- Sort by average duration descending""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["date-functions", "aggregation", "zoom"],
            "examples": [
                {
                    "explanation": "Meeting data with start times and durations. Calculate average by day of week.",
                    "sample_tables": {
                        "meetings": {
                            "meeting_id": "int",
                            "start_time": "timestamp",
                            "duration_minutes": "int",
                            "status": "varchar"
                        }
                    }
                }
            ],
            "solution": """SELECT 
  CASE EXTRACT(DOW FROM start_time)
    WHEN 0 THEN 'Sunday'
    WHEN 1 THEN 'Monday' 
    WHEN 2 THEN 'Tuesday'
    WHEN 3 THEN 'Wednesday'
    WHEN 4 THEN 'Thursday'
    WHEN 5 THEN 'Friday'
    WHEN 6 THEN 'Saturday'
  END as day_name,
  ROUND(AVG(duration_minutes), 1) as avg_duration
FROM meetings
WHERE status = 'completed'
GROUP BY EXTRACT(DOW FROM start_time)
ORDER BY avg_duration DESC;""",
            "test_cases": []
        },
        {
            "title": "DoorDash - Restaurant Performance Metrics",
            "description": """Write a query to calculate performance metrics for each restaurant. Output restaurant ID, total orders, average rating, and revenue per order.

Requirements:
- Only include restaurants with at least 50 orders
- Round average rating to 1 decimal place and revenue per order to 2 decimal places
- Sort by total orders descending""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["aggregation", "filtering", "doordash"],
            "examples": [
                {
                    "explanation": "Order data with restaurant info, ratings, and amounts. Calculate performance metrics.",
                    "sample_tables": {
                        "orders": {
                            "restaurant_id": "int",
                            "order_amount": "decimal",
                            "rating": "int",
                            "order_date": "date"
                        }
                    }
                }
            ],
            "solution": """WITH restaurant_metrics AS (
  SELECT 
    restaurant_id,
    COUNT(*) as total_orders,
    AVG(rating) as avg_rating,
    SUM(order_amount) / COUNT(*) as revenue_per_order
  FROM orders
  GROUP BY restaurant_id
  HAVING COUNT(*) >= 50
)

SELECT 
  restaurant_id,
  total_orders,
  ROUND(avg_rating, 1) as avg_rating,
  ROUND(revenue_per_order, 2) as revenue_per_order
FROM restaurant_metrics
ORDER BY total_orders DESC;""",
            "test_cases": []
        },
        {
            "title": "Salesforce - Lead Conversion Funnel",
            "description": """Write a query to analyze the lead conversion funnel by showing conversion rates at each stage. Output stage name and conversion rate as percentage.

Stages: lead -> opportunity -> customer
Notes:
- Conversion rate = (Count of current stage / Count of previous stage) * 100
- Round to 2 decimal places""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["funnel-analysis", "conversion", "salesforce"],
            "examples": [
                {
                    "explanation": "Lead tracking data showing progression through sales stages.",
                    "sample_tables": {
                        "leads": {
                            "lead_id": "int",
                            "stage": "varchar",
                            "created_date": "date"
                        }
                    }
                }
            ],
            "solution": """WITH stage_counts AS (
  SELECT 
    stage,
    COUNT(*) as count
  FROM leads
  GROUP BY stage
),

conversion_rates AS (
  SELECT 
    'lead_to_opportunity' as conversion_type,
    ROUND((SELECT count FROM stage_counts WHERE stage = 'opportunity') * 100.0 / 
          (SELECT count FROM stage_counts WHERE stage = 'lead'), 2) as conversion_rate
  UNION ALL
  SELECT 
    'opportunity_to_customer' as conversion_type,
    ROUND((SELECT count FROM stage_counts WHERE stage = 'customer') * 100.0 / 
          (SELECT count FROM stage_counts WHERE stage = 'opportunity'), 2) as conversion_rate
)

SELECT * FROM conversion_rates;""",
            "test_cases": []
        },
        {
            "title": "Pinterest - Pin Engagement by Category",
            "description": """Write a query to find the top 3 pin categories with highest average engagement per pin. Output category and average engagement rounded to 1 decimal place.

Definition:
- Engagement = saves + likes + clicks
- Only include categories with at least 100 pins""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["ranking", "engagement", "pinterest"],
            "examples": [
                {
                    "explanation": "Pin data with category and engagement metrics. Find top categories by average engagement.",
                    "sample_tables": {
                        "pins": {
                            "pin_id": "int",
                            "category": "varchar",
                            "saves": "int",
                            "likes": "int", 
                            "clicks": "int"
                        }
                    }
                }
            ],
            "solution": """WITH category_engagement AS (
  SELECT 
    category,
    COUNT(*) as total_pins,
    AVG(saves + likes + clicks) as avg_engagement
  FROM pins
  GROUP BY category
  HAVING COUNT(*) >= 100
)

SELECT 
  category,
  ROUND(avg_engagement, 1) as avg_engagement
FROM category_engagement
ORDER BY avg_engagement DESC
LIMIT 3;""",
            "test_cases": []
        },
        {
            "title": "Slack - Channel Activity Patterns",
            "description": """Write a query to identify peak activity hours for each channel. Output channel ID and the hour (0-23) with most messages.

Requirements:
- Use message timestamp to extract hour
- In case of ties, show the earliest hour
- Only include channels with at least 200 messages""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["time-analysis", "ranking", "slack"],
            "examples": [
                {
                    "explanation": "Message data with timestamps and channel info. Find peak activity hour per channel.",
                    "sample_tables": {
                        "messages": {
                            "channel_id": "int",
                            "message_timestamp": "timestamp",
                            "user_id": "int"
                        }
                    }
                }
            ],
            "solution": """WITH hourly_activity AS (
  SELECT 
    channel_id,
    EXTRACT(HOUR FROM message_timestamp) as hour,
    COUNT(*) as message_count
  FROM messages
  WHERE channel_id IN (
    SELECT channel_id 
    FROM messages 
    GROUP BY channel_id 
    HAVING COUNT(*) >= 200
  )
  GROUP BY channel_id, EXTRACT(HOUR FROM message_timestamp)
),

peak_hours AS (
  SELECT 
    channel_id,
    hour,
    message_count,
    ROW_NUMBER() OVER (PARTITION BY channel_id ORDER BY message_count DESC, hour ASC) as rank
  FROM hourly_activity
)

SELECT 
  channel_id,
  hour as peak_hour
FROM peak_hours
WHERE rank = 1;""",
            "test_cases": []
        },
        {
            "title": "Shopify - Monthly Sales Growth",
            "description": """Write a query to calculate month-over-month sales growth for each store. Output store ID, month, current month sales, previous month sales, and growth percentage.

Notes:
- Growth percentage = (Current - Previous) / Previous * 100
- Round growth percentage to 2 decimal places
- Show results for 2023 only""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["lag-lead", "growth", "shopify"],
            "examples": [
                {
                    "explanation": "Sales data by store and month. Calculate month-over-month growth rates.",
                    "sample_tables": {
                        "sales": {
                            "store_id": "int",
                            "sale_date": "date",
                            "sale_amount": "decimal"
                        }
                    }
                }
            ],
            "solution": """WITH monthly_sales AS (
  SELECT 
    store_id,
    DATE_TRUNC('month', sale_date) as month,
    SUM(sale_amount) as current_sales
  FROM sales
  WHERE EXTRACT(YEAR FROM sale_date) = 2023
  GROUP BY store_id, DATE_TRUNC('month', sale_date)
),

sales_with_previous AS (
  SELECT 
    store_id,
    month,
    current_sales,
    LAG(current_sales) OVER (PARTITION BY store_id ORDER BY month) as previous_sales
  FROM monthly_sales
)

SELECT 
  store_id,
  month,
  current_sales,
  previous_sales,
  CASE 
    WHEN previous_sales IS NULL THEN NULL
    ELSE ROUND(((current_sales - previous_sales) / previous_sales) * 100, 2)
  END as growth_percentage
FROM sales_with_previous
ORDER BY store_id, month;""",
            "test_cases": []
        },
        {
            "title": "Discord - Server Member Retention",
            "description": """Write a query to calculate 30-day member retention rate for each server. Output server ID and retention rate as percentage rounded to 2 decimal places.

Definition:
- Retention rate = (Members still active after 30 days / Total new members) * 100
- Consider a member active if they sent at least 1 message in days 30-35 after joining""",
            "category": "SQL",
            "difficulty": "Medium",
            "tags": ["retention", "date-range", "discord"],
            "examples": [
                {
                    "explanation": "Member join data and activity data. Calculate retention rates per server.",
                    "sample_tables": {
                        "members": {
                            "user_id": "int",
                            "server_id": "int",
                            "join_date": "date"
                        },
                        "activity": {
                            "user_id": "int",
                            "server_id": "int",
                            "activity_date": "date"
                        }
                    }
                }
            ],
            "solution": """WITH retention_analysis AS (
  SELECT 
    m.server_id,
    m.user_id,
    m.join_date,
    CASE 
      WHEN EXISTS (
        SELECT 1 FROM activity a 
        WHERE a.user_id = m.user_id 
        AND a.server_id = m.server_id
        AND a.activity_date BETWEEN (m.join_date + INTERVAL '30 days') 
                                 AND (m.join_date + INTERVAL '35 days')
      ) THEN 1 ELSE 0 
    END as retained
  FROM members m
  WHERE m.join_date <= CURRENT_DATE - INTERVAL '35 days'
)

SELECT 
  server_id,
  ROUND((SUM(retained) * 100.0 / COUNT(*)), 2) as retention_rate
FROM retention_analysis
GROUP BY server_id
ORDER BY retention_rate DESC;""",
            "test_cases": []
        }
    ]
    
    # Hard SQL Problems
    hard_sql_problems = [
        {
            "title": "Tesla - Manufacturing Defect Analysis",
            "description": """Analyze manufacturing defect patterns across production lines and shifts. Write a query to identify production lines where the defect rate increased by more than 20% compared to the previous shift, and calculate the rolling 7-shift average defect rate.

Requirements:
- Compare each shift's defect rate to the immediately previous shift on the same production line
- Include rolling 7-shift average defect rate
- Only show results where increase > 20%
- Sort by defect rate increase descending""",
            "category": "SQL",
            "difficulty": "Hard",
            "tags": ["manufacturing", "lag-lead", "rolling-average", "tesla"],
            "examples": [
                {
                    "explanation": "Production data with defect counts per shift and production line.",
                    "sample_tables": {
                        "production": {
                            "line_id": "int",
                            "shift_date": "date",
                            "shift_number": "int",
                            "units_produced": "int",
                            "defective_units": "int"
                        }
                    }
                }
            ],
            "solution": """WITH shift_defect_rates AS (
  SELECT 
    line_id,
    shift_date,
    shift_number,
    units_produced,
    defective_units,
    (defective_units * 100.0 / units_produced) as defect_rate,
    ROW_NUMBER() OVER (PARTITION BY line_id ORDER BY shift_date, shift_number) as shift_order
  FROM production
  WHERE units_produced > 0
),

defect_analysis AS (
  SELECT 
    line_id,
    shift_date,
    shift_number,
    defect_rate,
    LAG(defect_rate) OVER (PARTITION BY line_id ORDER BY shift_order) as prev_defect_rate,
    AVG(defect_rate) OVER (
      PARTITION BY line_id 
      ORDER BY shift_order 
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_7_avg_defect_rate
  FROM shift_defect_rates
),

significant_increases AS (
  SELECT 
    line_id,
    shift_date,
    shift_number,
    defect_rate,
    prev_defect_rate,
    rolling_7_avg_defect_rate,
    ((defect_rate - prev_defect_rate) / prev_defect_rate) * 100 as defect_increase_pct
  FROM defect_analysis
  WHERE prev_defect_rate IS NOT NULL
    AND prev_defect_rate > 0
    AND ((defect_rate - prev_defect_rate) / prev_defect_rate) > 0.20
)

SELECT 
  line_id,
  shift_date,
  shift_number,
  ROUND(defect_rate, 2) as current_defect_rate,
  ROUND(prev_defect_rate, 2) as previous_defect_rate,
  ROUND(rolling_7_avg_defect_rate, 2) as rolling_7_avg_defect_rate,
  ROUND(defect_increase_pct, 2) as defect_increase_percentage
FROM significant_increases
ORDER BY defect_increase_pct DESC;""",
            "test_cases": []
        },
        {
            "title": "Apple - Product Launch Success Prediction",
            "description": """Analyze product launch performance by calculating pre-launch buzz metrics and comparing them to actual sales performance. Identify products where social media engagement in the 30 days before launch correlates with first-month sales.

Requirements:
- Calculate total social engagement 30 days before launch
- Compare to actual first-month sales
- Classify launches as 'Exceeded', 'Met', or 'Below' expectations
- Include correlation coefficient between engagement and sales for each product category""",
            "category": "SQL",
            "difficulty": "Hard",
            "tags": ["correlation", "window-functions", "apple"],
            "examples": [
                {
                    "explanation": "Product launch data, social media engagement, and sales data.",
                    "sample_tables": {
                        "products": {
                            "product_id": "int",
                            "category": "varchar",
                            "launch_date": "date",
                            "expected_first_month_sales": "int"
                        },
                        "social_engagement": {
                            "product_id": "int",
                            "engagement_date": "date",
                            "mentions": "int",
                            "sentiment_score": "decimal"
                        },
                        "sales": {
                            "product_id": "int",
                            "sale_date": "date",
                            "units_sold": "int"
                        }
                    }
                }
            ],
            "solution": """WITH pre_launch_engagement AS (
  SELECT 
    p.product_id,
    p.category,
    p.launch_date,
    p.expected_first_month_sales,
    SUM(se.mentions * se.sentiment_score) as total_engagement_score
  FROM products p
  LEFT JOIN social_engagement se ON p.product_id = se.product_id
    AND se.engagement_date BETWEEN (p.launch_date - INTERVAL '30 days') AND p.launch_date
  GROUP BY p.product_id, p.category, p.launch_date, p.expected_first_month_sales
),

actual_first_month_sales AS (
  SELECT 
    p.product_id,
    SUM(s.units_sold) as actual_sales
  FROM products p
  LEFT JOIN sales s ON p.product_id = s.product_id
    AND s.sale_date BETWEEN p.launch_date AND (p.launch_date + INTERVAL '30 days')
  GROUP BY p.product_id
),

launch_performance AS (
  SELECT 
    ple.*,
    afms.actual_sales,
    CASE 
      WHEN afms.actual_sales > ple.expected_first_month_sales * 1.1 THEN 'Exceeded'
      WHEN afms.actual_sales >= ple.expected_first_month_sales * 0.9 THEN 'Met'
      ELSE 'Below'
    END as performance_category,
    (afms.actual_sales / ple.expected_first_month_sales) as performance_ratio
  FROM pre_launch_engagement ple
  LEFT JOIN actual_first_month_sales afms ON ple.product_id = afms.product_id
),

category_correlations AS (
  SELECT 
    category,
    COUNT(*) as product_count,
    CORR(total_engagement_score, actual_sales) as engagement_sales_correlation
  FROM launch_performance
  WHERE total_engagement_score IS NOT NULL AND actual_sales IS NOT NULL
  GROUP BY category
)

SELECT 
  lp.product_id,
  lp.category,
  lp.launch_date,
  COALESCE(lp.total_engagement_score, 0) as pre_launch_engagement,
  lp.expected_first_month_sales,
  COALESCE(lp.actual_sales, 0) as actual_first_month_sales,
  lp.performance_category,
  ROUND(lp.performance_ratio, 2) as performance_ratio,
  ROUND(cc.engagement_sales_correlation, 3) as category_correlation
FROM launch_performance lp
LEFT JOIN category_correlations cc ON lp.category = cc.category
ORDER BY lp.performance_ratio DESC;""",
            "test_cases": []
        },
        {
            "title": "Amazon - Dynamic Pricing Impact Analysis",
            "description": """Analyze the impact of dynamic pricing on sales and revenue. Calculate price elasticity for each product and identify optimal pricing windows where revenue was maximized.

Requirements:
- Calculate price elasticity: % change in quantity / % change in price
- Find 7-day windows with maximum revenue for each product
- Include competitor price comparison during peak revenue periods
- Only include products with at least 10 price changes""",
            "category": "SQL",
            "difficulty": "Hard",
            "tags": ["elasticity", "optimization", "amazon"],
            "examples": [
                {
                    "explanation": "Product pricing history, sales data, and competitor prices.",
                    "sample_tables": {
                        "pricing_history": {
                            "product_id": "int",
                            "price_date": "date",
                            "price": "decimal"
                        },
                        "sales_data": {
                            "product_id": "int",
                            "sale_date": "date",
                            "quantity_sold": "int"
                        },
                        "competitor_prices": {
                            "product_id": "int",
                            "price_date": "date",
                            "competitor_price": "decimal"
                        }
                    }
                }
            ],
            "solution": """WITH price_changes AS (
  SELECT 
    product_id,
    price_date,
    price,
    LAG(price) OVER (PARTITION BY product_id ORDER BY price_date) as prev_price,
    LAG(price_date) OVER (PARTITION BY product_id ORDER BY price_date) as prev_price_date
  FROM pricing_history
),

daily_sales AS (
  SELECT 
    product_id,
    sale_date,
    SUM(quantity_sold) as daily_quantity
  FROM sales_data
  GROUP BY product_id, sale_date
),

sales_with_prices AS (
  SELECT 
    s.product_id,
    s.sale_date,
    s.daily_quantity,
    p.price,
    LAG(s.daily_quantity) OVER (PARTITION BY s.product_id ORDER BY s.sale_date) as prev_quantity,
    LAG(p.price) OVER (PARTITION BY s.product_id ORDER BY s.sale_date) as prev_price
  FROM daily_sales s
  JOIN pricing_history p ON s.product_id = p.product_id AND s.sale_date = p.price_date
),

elasticity_calculation AS (
  SELECT 
    product_id,
    sale_date,
    price,
    daily_quantity,
    CASE 
      WHEN prev_price > 0 AND prev_quantity > 0 AND prev_price != price THEN
        ((daily_quantity - prev_quantity) / prev_quantity) / 
        ((price - prev_price) / prev_price)
      ELSE NULL
    END as price_elasticity
  FROM sales_with_prices
  WHERE prev_price IS NOT NULL AND prev_quantity IS NOT NULL
),

revenue_windows AS (
  SELECT 
    s.product_id,
    s.sale_date,
    s.daily_quantity * p.price as daily_revenue,
    SUM(s.daily_quantity * p.price) OVER (
      PARTITION BY s.product_id 
      ORDER BY s.sale_date 
      ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    ) as window_7_revenue
  FROM daily_sales s
  JOIN pricing_history p ON s.product_id = p.product_id AND s.sale_date = p.price_date
),

max_revenue_windows AS (
  SELECT 
    product_id,
    sale_date,
    window_7_revenue,
    ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY window_7_revenue DESC) as revenue_rank
  FROM revenue_windows
),

qualified_products AS (
  SELECT product_id
  FROM pricing_history
  GROUP BY product_id
  HAVING COUNT(DISTINCT price) >= 10
)

SELECT 
  e.product_id,
  ROUND(AVG(e.price_elasticity), 3) as avg_price_elasticity,
  mrw.sale_date as peak_revenue_date,
  ROUND(mrw.window_7_revenue, 2) as peak_7day_revenue,
  ROUND(p.price, 2) as price_during_peak,
  ROUND(cp.competitor_price, 2) as competitor_price_during_peak,
  ROUND((p.price - cp.competitor_price) / cp.competitor_price * 100, 2) as price_premium_pct
FROM elasticity_calculation e
JOIN qualified_products qp ON e.product_id = qp.product_id
JOIN max_revenue_windows mrw ON e.product_id = mrw.product_id AND mrw.revenue_rank = 1
JOIN pricing_history p ON mrw.product_id = p.product_id AND mrw.sale_date = p.price_date
LEFT JOIN competitor_prices cp ON mrw.product_id = cp.product_id AND mrw.sale_date = cp.price_date
WHERE e.price_elasticity IS NOT NULL
GROUP BY e.product_id, mrw.sale_date, mrw.window_7_revenue, p.price, cp.competitor_price
ORDER BY avg_price_elasticity;""",
            "test_cases": []
        },
        {
            "title": "Google - Search Query Performance Optimization",
            "description": """Analyze search query performance to identify opportunities for optimization. Calculate query success rates, user satisfaction scores, and identify queries with declining performance trends.

Requirements:
- Calculate weekly query success rates and trends
- Identify queries with >15% decline in success rate over 4 weeks  
- Include user satisfaction correlation with result click-through rates
- Generate recommendations based on query patterns""",
            "category": "SQL",
            "difficulty": "Hard",
            "tags": ["trend-analysis", "correlation", "google"],
            "examples": [
                {
                    "explanation": "Search query data, user interactions, and satisfaction metrics.",
                    "sample_tables": {
                        "search_queries": {
                            "query_id": "int",
                            "query_text": "varchar",
                            "search_date": "timestamp",
                            "user_id": "int"
                        },
                        "query_results": {
                            "query_id": "int",
                            "result_position": "int",
                            "clicked": "boolean",
                            "time_on_result": "int"
                        },
                        "user_feedback": {
                            "query_id": "int",
                            "satisfaction_score": "int"
                        }
                    }
                }
            ],
            "solution": """WITH weekly_query_performance AS (
  SELECT 
    sq.query_text,
    DATE_TRUNC('week', sq.search_date) as week_start,
    COUNT(DISTINCT sq.query_id) as total_queries,
    COUNT(DISTINCT CASE WHEN qr.clicked THEN sq.query_id END) as successful_queries,
    AVG(uf.satisfaction_score) as avg_satisfaction,
    AVG(CASE WHEN qr.clicked THEN qr.time_on_result END) as avg_time_on_result
  FROM search_queries sq
  LEFT JOIN query_results qr ON sq.query_id = qr.query_id
  LEFT JOIN user_feedback uf ON sq.query_id = uf.query_id
  GROUP BY sq.query_text, DATE_TRUNC('week', sq.search_date)
  HAVING COUNT(DISTINCT sq.query_id) >= 100
),

query_trends AS (
  SELECT 
    query_text,
    week_start,
    total_queries,
    (successful_queries * 100.0 / total_queries) as success_rate,
    avg_satisfaction,
    avg_time_on_result,
    LAG(successful_queries * 100.0 / total_queries, 1) OVER (
      PARTITION BY query_text ORDER BY week_start
    ) as prev_week_success_rate,
    LAG(successful_queries * 100.0 / total_queries, 4) OVER (
      PARTITION BY query_text ORDER BY week_start
    ) as four_weeks_ago_success_rate
  FROM weekly_query_performance
),

declining_queries AS (
  SELECT 
    query_text,
    week_start,
    success_rate,
    four_weeks_ago_success_rate,
    avg_satisfaction,
    avg_time_on_result,
    (success_rate - four_weeks_ago_success_rate) as success_rate_change,
    ((success_rate - four_weeks_ago_success_rate) / four_weeks_ago_success_rate) * 100 as success_rate_change_pct
  FROM query_trends
  WHERE four_weeks_ago_success_rate IS NOT NULL
    AND four_weeks_ago_success_rate > 0
    AND ((success_rate - four_weeks_ago_success_rate) / four_weeks_ago_success_rate) < -0.15
),

query_patterns AS (
  SELECT 
    dq.query_text,
    dq.success_rate_change_pct,
    dq.avg_satisfaction,
    dq.avg_time_on_result,
    CASE 
      WHEN LENGTH(dq.query_text) > 50 THEN 'Long Query'
      WHEN dq.query_text ~ '[?]' THEN 'Question'
      WHEN dq.query_text ~ '^(how|what|when|where|why|who)' THEN 'Informational'
      ELSE 'General'
    END as query_category,
    CORR(dq.success_rate, dq.avg_satisfaction) OVER (
      PARTITION BY CASE 
        WHEN LENGTH(dq.query_text) > 50 THEN 'Long Query'
        WHEN dq.query_text ~ '[?]' THEN 'Question'  
        WHEN dq.query_text ~ '^(how|what|when|where|why|who)' THEN 'Informational'
        ELSE 'General'
      END
    ) as category_satisfaction_correlation
  FROM declining_queries dq
)

SELECT 
  query_text,
  ROUND(success_rate_change_pct, 2) as success_decline_pct,
  ROUND(avg_satisfaction, 2) as avg_satisfaction,
  ROUND(avg_time_on_result, 1) as avg_time_on_result_seconds,
  query_category,
  ROUND(category_satisfaction_correlation, 3) as satisfaction_correlation,
  CASE 
    WHEN avg_satisfaction < 3.0 AND avg_time_on_result < 30 THEN 'Improve result relevance'
    WHEN query_category = 'Long Query' THEN 'Implement query suggestions'
    WHEN query_category = 'Question' THEN 'Enhance direct answers'
    ELSE 'Standard optimization'
  END as optimization_recommendation
FROM query_patterns
ORDER BY success_decline_pct ASC;""",
            "test_cases": []
        },
        {
            "title": "Netflix - Content Recommendation Engine Analysis",
            "description": """Analyze the effectiveness of Netflix's recommendation engine by examining user engagement patterns, content discovery rates, and recommendation conversion metrics across different user segments.

Requirements:
- Calculate recommendation conversion rates by user segment and content type
- Identify content with highest discovery-to-completion ratios
- Analyze seasonal viewing pattern impact on recommendations
- Find optimal recommendation list size for each user segment""",
            "category": "SQL",
            "difficulty": "Hard",
            "tags": ["recommendation-engine", "segmentation", "netflix"],
            "examples": [
                {
                    "explanation": "User viewing data, recommendations, and content metadata.",
                    "sample_tables": {
                        "users": {
                            "user_id": "int",
                            "age_group": "varchar",
                            "subscription_type": "varchar",
                            "region": "varchar"
                        },
                        "recommendations": {
                            "user_id": "int",
                            "content_id": "int",
                            "recommendation_date": "date",
                            "position_in_list": "int",
                            "recommendation_type": "varchar"
                        },
                        "viewing_activity": {
                            "user_id": "int",
                            "content_id": "int",
                            "watch_date": "timestamp",
                            "completion_percentage": "decimal"
                        },
                        "content": {
                            "content_id": "int",
                            "title": "varchar",
                            "genre": "varchar",
                            "content_type": "varchar",
                            "release_year": "int"
                        }
                    }
                }
            ],
            "solution": """WITH user_segments AS (
  SELECT 
    user_id,
    age_group,
    subscription_type,
    region,
    CONCAT(age_group, '_', subscription_type) as segment
  FROM users
),

recommendation_performance AS (
  SELECT 
    r.user_id,
    r.content_id,
    r.recommendation_date,
    r.position_in_list,
    r.recommendation_type,
    c.genre,
    c.content_type,
    us.segment,
    CASE WHEN va.user_id IS NOT NULL THEN 1 ELSE 0 END as was_watched,
    COALESCE(va.completion_percentage, 0) as completion_pct,
    EXTRACT(QUARTER FROM r.recommendation_date) as recommendation_quarter
  FROM recommendations r
  JOIN content c ON r.content_id = c.content_id
  JOIN user_segments us ON r.user_id = us.user_id
  LEFT JOIN viewing_activity va ON r.user_id = va.user_id 
    AND r.content_id = va.content_id
    AND va.watch_date BETWEEN r.recommendation_date AND (r.recommendation_date + INTERVAL '30 days')
),

segment_conversion_rates AS (
  SELECT 
    segment,
    content_type,
    recommendation_quarter,
    COUNT(*) as total_recommendations,
    SUM(was_watched) as watched_count,
    AVG(CASE WHEN was_watched = 1 THEN completion_pct END) as avg_completion_when_watched,
    (SUM(was_watched) * 100.0 / COUNT(*)) as conversion_rate
  FROM recommendation_performance
  GROUP BY segment, content_type, recommendation_quarter
),

position_effectiveness AS (
  SELECT 
    segment,
    position_in_list,
    COUNT(*) as recommendations_at_position,
    SUM(was_watched) as watches_at_position,
    (SUM(was_watched) * 100.0 / COUNT(*)) as position_conversion_rate
  FROM recommendation_performance
  WHERE position_in_list <= 20
  GROUP BY segment, position_in_list
),

optimal_list_size AS (
  SELECT 
    segment,
    position_in_list,
    position_conversion_rate,
    SUM(recommendations_at_position) OVER (
      PARTITION BY segment 
      ORDER BY position_in_list 
      ROWS UNBOUNDED PRECEDING
    ) as cumulative_recommendations,
    SUM(watches_at_position) OVER (
      PARTITION BY segment 
      ORDER BY position_in_list 
      ROWS UNBOUNDED PRECEDING
    ) as cumulative_watches
  FROM position_effectiveness
),

content_discovery_rates AS (
  SELECT 
    c.title,
    c.genre,
    c.content_type,
    COUNT(DISTINCT rp.user_id) as total_recommended_users,
    COUNT(DISTINCT CASE WHEN rp.was_watched = 1 THEN rp.user_id END) as discovery_users,
    AVG(CASE WHEN rp.was_watched = 1 THEN rp.completion_pct END) as avg_completion,
    (COUNT(DISTINCT CASE WHEN rp.was_watched = 1 THEN rp.user_id END) * 100.0 / 
     COUNT(DISTINCT rp.user_id)) as discovery_rate
  FROM content c
  JOIN recommendation_performance rp ON c.content_id = rp.content_id
  GROUP BY c.content_id, c.title, c.genre, c.content_type
  HAVING COUNT(DISTINCT rp.user_id) >= 1000
)

SELECT 
  'SEGMENT_PERFORMANCE' as analysis_type,
  scr.segment,
  scr.content_type,
  ROUND(AVG(scr.conversion_rate), 2) as avg_conversion_rate,
  ROUND(AVG(scr.avg_completion_when_watched), 1) as avg_completion_rate,
  NULL as title,
  NULL as discovery_rate,
  NULL as optimal_list_size
FROM segment_conversion_rates scr
GROUP BY scr.segment, scr.content_type

UNION ALL

SELECT 
  'CONTENT_DISCOVERY' as analysis_type,
  NULL as segment,
  cdr.content_type,
  NULL as avg_conversion_rate,
  ROUND(cdr.avg_completion, 1) as avg_completion_rate,
  cdr.title,
  ROUND(cdr.discovery_rate, 2) as discovery_rate,
  NULL as optimal_list_size
FROM content_discovery_rates cdr
WHERE cdr.discovery_rate >= 15

UNION ALL

SELECT 
  'OPTIMAL_LIST_SIZE' as analysis_type,
  ols.segment,
  NULL as content_type,
  NULL as avg_conversion_rate,
  NULL as avg_completion_rate,
  NULL as title,
  NULL as discovery_rate,
  MIN(CASE WHEN (ols.cumulative_watches * 100.0 / ols.cumulative_recommendations) >= 80 
       THEN ols.position_in_list END) as optimal_list_size
FROM optimal_list_size ols
GROUP BY ols.segment

ORDER BY analysis_type, segment, content_type;""",
            "test_cases": []
        },
        {
            "title": "Spotify - Music Discovery and Artist Success Prediction",
            "description": """Build a comprehensive analysis to predict artist success by analyzing music discovery patterns, user engagement metrics, and playlist inclusion rates across different user demographics and geographic regions.

Requirements:
- Calculate artist momentum score based on weekly growth in streams, followers, and playlist adds
- Identify emerging artists with high discovery-to-retention conversion rates
- Analyze the correlation between playlist placement and long-term artist success
- Predict breakthrough potential using multi-factor scoring""",
            "category": "SQL",
            "difficulty": "Hard",
            "tags": ["prediction", "discovery", "spotify"],
            "examples": [
                {
                    "explanation": "Comprehensive music streaming data including artists, tracks, user behavior, and playlist information.",
                    "sample_tables": {
                        "artists": {
                            "artist_id": "int",
                            "artist_name": "varchar",
                            "genre": "varchar",
                            "debut_date": "date"
                        },
                        "tracks": {
                            "track_id": "int",
                            "artist_id": "int",
                            "release_date": "date"
                        },
                        "streams": {
                            "user_id": "int",
                            "track_id": "int",
                            "stream_date": "timestamp",
                            "completion_percentage": "decimal"
                        },
                        "playlist_inclusions": {
                            "playlist_id": "int",
                            "track_id": "int",
                            "added_date": "date",
                            "playlist_type": "varchar"
                        }
                    }
                }
            ],
            "solution": """WITH weekly_artist_metrics AS (
  SELECT 
    a.artist_id,
    a.artist_name,
    a.genre,
    DATE_TRUNC('week', s.stream_date) as week_start,
    COUNT(DISTINCT s.user_id) as unique_listeners,
    COUNT(*) as total_streams,
    AVG(s.completion_percentage) as avg_completion_rate,
    COUNT(DISTINCT t.track_id) as active_tracks
  FROM artists a
  JOIN tracks t ON a.artist_id = t.artist_id
  JOIN streams s ON t.track_id = s.track_id
  WHERE s.stream_date >= CURRENT_DATE - INTERVAL '12 weeks'
  GROUP BY a.artist_id, a.artist_name, a.genre, DATE_TRUNC('week', s.stream_date)
),

artist_growth_trends AS (
  SELECT 
    artist_id,
    artist_name,
    genre,
    week_start,
    unique_listeners,
    total_streams,
    avg_completion_rate,
    LAG(unique_listeners, 1) OVER (PARTITION BY artist_id ORDER BY week_start) as prev_week_listeners,
    LAG(total_streams, 1) OVER (PARTITION BY artist_id ORDER BY week_start) as prev_week_streams,
    LAG(unique_listeners, 4) OVER (PARTITION BY artist_id ORDER BY week_start) as four_weeks_ago_listeners,
    LAG(total_streams, 4) OVER (PARTITION BY artist_id ORDER BY week_start) as four_weeks_ago_streams
  FROM weekly_artist_metrics
),

momentum_calculation AS (
  SELECT 
    artist_id,
    artist_name,
    genre,
    week_start,
    unique_listeners,
    total_streams,
    avg_completion_rate,
    CASE 
      WHEN prev_week_listeners > 0 THEN 
        ((unique_listeners - prev_week_listeners) / prev_week_listeners * 100)
      ELSE 0 
    END as weekly_listener_growth,
    CASE 
      WHEN four_weeks_ago_streams > 0 THEN 
        ((total_streams - four_weeks_ago_streams) / four_weeks_ago_streams * 100)
      ELSE 0 
    END as monthly_stream_growth
  FROM artist_growth_trends
),

playlist_impact AS (
  SELECT 
    a.artist_id,
    COUNT(DISTINCT pi.playlist_id) as total_playlist_inclusions,
    COUNT(DISTINCT CASE WHEN pi.playlist_type = 'editorial' THEN pi.playlist_id END) as editorial_inclusions,
    COUNT(DISTINCT CASE WHEN pi.playlist_type = 'algorithmic' THEN pi.playlist_id END) as algorithmic_inclusions,
    AVG(DATE_PART('day', CURRENT_DATE - pi.added_date)) as avg_days_since_playlist_add
  FROM artists a
  JOIN tracks t ON a.artist_id = t.artist_id
  JOIN playlist_inclusions pi ON t.track_id = pi.track_id
  WHERE pi.added_date >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY a.artist_id
),

discovery_metrics AS (
  SELECT 
    a.artist_id,
    COUNT(DISTINCT CASE WHEN s.completion_percentage >= 0.8 THEN s.user_id END) as high_engagement_users,
    COUNT(DISTINCT s.user_id) as total_discoverers,
    COUNT(DISTINCT CASE WHEN user_stream_count >= 5 THEN s.user_id END) as retained_listeners
  FROM artists a
  JOIN tracks t ON a.artist_id = t.artist_id
  JOIN (
    SELECT 
      user_id, 
      track_id, 
      completion_percentage,
      COUNT(*) OVER (PARTITION BY user_id, track_id) as user_stream_count
    FROM streams 
    WHERE stream_date >= CURRENT_DATE - INTERVAL '30 days'
  ) s ON t.track_id = s.track_id
  GROUP BY a.artist_id
),

artist_success_score AS (
  SELECT 
    mc.artist_id,
    mc.artist_name,
    mc.genre,
    AVG(mc.weekly_listener_growth) as avg_weekly_growth,
    AVG(mc.monthly_stream_growth) as avg_monthly_growth,
    AVG(mc.avg_completion_rate) as overall_completion_rate,
    pi.total_playlist_inclusions,
    pi.editorial_inclusions,
    (dm.retained_listeners * 100.0 / NULLIF(dm.total_discoverers, 0)) as discovery_retention_rate,
    (dm.high_engagement_users * 100.0 / NULLIF(dm.total_discoverers, 0)) as engagement_rate
  FROM momentum_calculation mc
  LEFT JOIN playlist_impact pi ON mc.artist_id = pi.artist_id
  LEFT JOIN discovery_metrics dm ON mc.artist_id = dm.artist_id
  WHERE mc.week_start >= CURRENT_DATE - INTERVAL '8 weeks'
  GROUP BY mc.artist_id, mc.artist_name, mc.genre, 
           pi.total_playlist_inclusions, pi.editorial_inclusions,
           dm.retained_listeners, dm.total_discoverers, dm.high_engagement_users
),

breakthrough_prediction AS (
  SELECT 
    artist_id,
    artist_name,
    genre,
    ROUND(avg_weekly_growth, 2) as avg_weekly_listener_growth,
    ROUND(avg_monthly_growth, 2) as avg_monthly_stream_growth,
    ROUND(overall_completion_rate, 3) as completion_rate,
    COALESCE(total_playlist_inclusions, 0) as playlist_count,
    COALESCE(editorial_inclusions, 0) as editorial_playlist_count,
    ROUND(COALESCE(discovery_retention_rate, 0), 2) as discovery_retention_pct,
    ROUND(COALESCE(engagement_rate, 0), 2) as high_engagement_pct,
    -- Multi-factor breakthrough score
    (COALESCE(avg_weekly_growth, 0) * 0.25 +
     COALESCE(avg_monthly_growth, 0) * 0.15 +
     COALESCE(overall_completion_rate * 100, 0) * 0.2 +
     COALESCE(total_playlist_inclusions, 0) * 2 +
     COALESCE(editorial_inclusions, 0) * 5 +
     COALESCE(discovery_retention_rate, 0) * 0.3 +
     COALESCE(engagement_rate, 0) * 0.1) as breakthrough_score
  FROM artist_success_score
)

SELECT 
  artist_name,
  genre,
  avg_weekly_listener_growth,
  avg_monthly_stream_growth,
  completion_rate,
  playlist_count,
  editorial_playlist_count,
  discovery_retention_pct,
  high_engagement_pct,
  ROUND(breakthrough_score, 2) as breakthrough_score,
  CASE 
    WHEN breakthrough_score >= 100 THEN 'High Breakthrough Potential'
    WHEN breakthrough_score >= 50 THEN 'Moderate Breakthrough Potential'
    WHEN breakthrough_score >= 20 THEN 'Emerging Artist'
    ELSE 'Developing'
  END as success_prediction
FROM breakthrough_prediction
WHERE breakthrough_score > 0
ORDER BY breakthrough_score DESC
LIMIT 50;""",
            "test_cases": []
        }
    ]
    
    # Combine all problems
    all_problems = medium_sql_problems + hard_sql_problems
    
    # Insert problems into database
    for problem in all_problems:
        cursor.execute("""
            INSERT INTO problems (
                title, description, examples, constraints, difficulty, 
                category, tags, test_cases, solution_template, acceptance_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            problem['title'],
            problem['description'],
            json.dumps(problem['examples']),
            json.dumps([]),  # constraints
            problem['difficulty'],
            problem['category'],
            json.dumps(problem['tags']),
            json.dumps(problem['test_cases']),
            json.dumps({
                'sql': problem['solution']
            }),
            75.0  # default acceptance rate
        ))
    
    conn.commit()
    print(f"Added {len(all_problems)} SQL problems to the database!")
    
    # Show what was added
    cursor.execute("SELECT id, title, difficulty, category FROM problems WHERE category = 'SQL' ORDER BY id DESC")
    new_problems = cursor.fetchall()
    print("\nAdded problems:")
    for p in new_problems:
        print(f"  {p[0]}: {p[1]} ({p[2]}, {p[3]})")
    
    conn.close()

if __name__ == "__main__":
    add_sql_problems()