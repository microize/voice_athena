#!/usr/bin/env python3
"""
Script to update SQL problems with proper table schemas and example data
"""

import sqlite3
import json
from datetime import datetime

def update_sql_problems():
    conn = sqlite3.connect('../data/interview_sessions.db')
    cursor = conn.cursor()
    
    # Updated SQL problems with proper schemas and examples
    updated_problems = [
        {
            "id": 5,
            "title": "Netflix - User's Fourth Favorite Movie",
            "description": """Given a table of user viewing data, find the fourth most-watched movie for each user based on total watch time.

Write a query to obtain the fourth most-watched movie for each user. Output the user ID, movie title, and total watch time.

**Assumptions:**
- A user's most-watched movie is determined by total watch time
- If a user has watched fewer than 4 movies, exclude them from results
- Users can watch the same movie multiple times

**user_viewing Table:**
| Column Name | Type |
|-------------|------|
| user_id | integer |
| movie_title | varchar |
| watch_time_minutes | integer |

**user_viewing Example Input:**
| user_id | movie_title | watch_time_minutes |
|---------|-------------|-------------------|
| 101 | Stranger Things | 240 |
| 101 | The Crown | 180 |
| 101 | Ozark | 300 |
| 101 | House of Cards | 150 |
| 101 | Dark | 200 |
| 102 | The Witcher | 220 |
| 102 | Narcos | 190 |

**Example Output:**
| user_id | movie_title | watch_time_minutes |
|---------|-------------|-------------------|
| 101 | Dark | 200 |

**Explanation:**
User 101's movies ranked by watch time: 1) Ozark (300), 2) Stranger Things (240), 3) Dark (200), 4) The Crown (180), 5) House of Cards (150). The 4th most-watched is Dark with 200 minutes.

User 102 only has 2 movies, so they're excluded from results.""",
            "examples": [
                {
                    "input": "user_viewing table with viewing data",
                    "output": "Users with their 4th most watched movies",
                    "explanation": "Use ROW_NUMBER() window function to rank movies by watch time per user, then filter for rank 4"
                }
            ]
        },
        {
            "id": 6,
            "title": "PayPal - Transaction Success vs Failure Rate",
            "description": """Given a table of payment transactions, calculate the success and failure rates for each payment method.

Write a query to calculate the percentage breakdown of successful vs failed transactions for each payment method. Round percentages to 2 decimal places.

**Notes:**
- Success rate = (Successful transactions / Total transactions) × 100
- Failure rate = (Failed transactions / Total transactions) × 100

**transactions Table:**
| Column Name | Type |
|-------------|------|
| transaction_id | integer |
| payment_method | varchar |
| status | varchar |
| amount | decimal |

**transactions Example Input:**
| transaction_id | payment_method | status | amount |
|---------------|----------------|---------|--------|
| 1001 | credit_card | success | 150.00 |
| 1002 | credit_card | failed | 89.99 |
| 1003 | paypal | success | 299.99 |
| 1004 | credit_card | success | 199.50 |
| 1005 | paypal | failed | 75.00 |
| 1006 | paypal | success | 120.00 |

**Example Output:**
| payment_method | success_rate | failure_rate |
|---------------|--------------|--------------|
| credit_card | 66.67 | 33.33 |
| paypal | 66.67 | 33.33 |

**Explanation:**
Credit card: 2 success out of 3 total = 66.67% success, 33.33% failure
PayPal: 2 success out of 3 total = 66.67% success, 33.33% failure""",
            "examples": [
                {
                    "input": "transactions table with payment data",
                    "output": "Success and failure rates per payment method",
                    "explanation": "Use conditional aggregation with CASE statements to calculate success/failure counts"
                }
            ]
        },
        {
            "id": 7,
            "title": "LinkedIn - Connection Growth Trend",
            "description": """Given a table of daily new connections for LinkedIn users, calculate the 7-day rolling average of new connections for each user.

Write a query to calculate the 7-day rolling average of new connections for each user. Output user ID, date, and rolling average rounded to 2 decimal places.

**Notes:**
- Rolling average should include current day and 6 preceding days
- Only include users who have made connections on at least 7 different days

**connections Table:**
| Column Name | Type |
|-------------|------|
| user_id | integer |
| connection_date | date |
| new_connections | integer |

**connections Example Input:**
| user_id | connection_date | new_connections |
|---------|----------------|-----------------|
| 1 | 2023-01-01 | 5 |
| 1 | 2023-01-02 | 3 |
| 1 | 2023-01-03 | 7 |
| 1 | 2023-01-04 | 2 |
| 1 | 2023-01-05 | 8 |
| 1 | 2023-01-06 | 4 |
| 1 | 2023-01-07 | 6 |
| 1 | 2023-01-08 | 1 |

**Example Output:**
| user_id | connection_date | rolling_avg_7_days |
|---------|----------------|-------------------|
| 1 | 2023-01-07 | 5.00 |
| 1 | 2023-01-08 | 4.43 |

**Explanation:**
For 2023-01-07: Average of (5+3+7+2+8+4+6) / 7 = 5.00
For 2023-01-08: Average of (3+7+2+8+4+6+1) / 7 = 4.43""",
            "examples": [
                {
                    "input": "connections table with daily connection data",
                    "output": "7-day rolling averages per user",
                    "explanation": "Use AVG() window function with ROWS BETWEEN 6 PRECEDING AND CURRENT ROW"
                }
            ]
        },
        {
            "id": 8,
            "title": "Airbnb - Top 2 Host Properties by Revenue",
            "description": """Given a table of Airbnb bookings, find the top 2 highest revenue-generating properties for each host in 2023.

Write a query to find the top 2 highest revenue-generating properties for each host in 2023. Output host ID, property ID, and total revenue.

**Assumptions:**
- Revenue is calculated as sum of all booking amounts for the property
- If a host has fewer than 2 properties, show all their properties
- Only consider bookings from 2023

**bookings Table:**
| Column Name | Type |
|-------------|------|
| booking_id | integer |
| host_id | integer |
| property_id | integer |
| booking_amount | decimal |
| booking_date | date |

**bookings Example Input:**
| booking_id | host_id | property_id | booking_amount | booking_date |
|-----------|---------|-------------|----------------|--------------|
| 1 | 101 | 201 | 150.00 | 2023-03-15 |
| 2 | 101 | 202 | 200.00 | 2023-04-10 |
| 3 | 101 | 201 | 175.00 | 2023-05-20 |
| 4 | 101 | 203 | 300.00 | 2023-06-15 |
| 5 | 102 | 204 | 180.00 | 2023-07-01 |

**Example Output:**
| host_id | property_id | total_revenue |
|---------|-------------|---------------|
| 101 | 201 | 325.00 |
| 101 | 203 | 300.00 |
| 102 | 204 | 180.00 |

**Explanation:**
Host 101: Property 201 ($325), Property 203 ($300), Property 202 ($200). Top 2 are 201 and 203.
Host 102: Only has one property (204), so it's included.""",
            "examples": [
                {
                    "input": "bookings table with property and revenue data",
                    "output": "Top 2 revenue properties per host",
                    "explanation": "Use ROW_NUMBER() window function to rank properties by revenue per host"
                }
            ]
        }
    ]
    
    print(f"Updating {len(updated_problems)} SQL problems with proper schemas...")
    
    for problem_data in updated_problems:
        problem_id = problem_data["id"]
        new_description = problem_data["description"]
        new_examples = json.dumps(problem_data["examples"])
        
        cursor.execute("""
            UPDATE problems 
            SET description = ?, examples = ?
            WHERE id = ?
        """, (new_description, new_examples, problem_id))
        
        print(f"  ✓ Updated problem {problem_id}: {problem_data['title']}")
    
    conn.commit()
    print(f"\n✅ Successfully updated {len(updated_problems)} SQL problems with schemas!")
    
    # Verify one update
    print("\nVerifying update...")
    cursor.execute("SELECT title, description FROM problems WHERE id = 5")
    result = cursor.fetchone()
    if result:
        print(f"Problem: {result[0]}")
        print(f"Description preview: {result[1][:200]}...")
    
    conn.close()

if __name__ == "__main__":
    update_sql_problems()