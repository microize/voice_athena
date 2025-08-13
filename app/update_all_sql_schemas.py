#!/usr/bin/env python3
"""
Script to update ALL SQL problems with proper table schemas and example data
"""

import sqlite3
import json

def update_all_sql_problems():
    conn = sqlite3.connect('interview_sessions.db')
    cursor = conn.cursor()
    
    # Get all SQL problems
    cursor.execute("SELECT id, title FROM problems WHERE category = 'SQL' ORDER BY id")
    sql_problems = cursor.fetchall()
    
    # Comprehensive updates for all SQL problems
    problem_updates = {
        9: {
            "title": "Instagram - Engagement Rate Analysis",
            "description": """Given tables of Instagram posts and users, calculate the engagement rate for each user's posts.

Write a query to calculate the engagement rate for each user's posts. Output user ID and engagement rate as a percentage rounded to 2 decimal places.

**Definition:**
- Engagement rate = (Total Likes + Total Comments) / Followers × 100
- Only include users with at least 1000 followers

**posts Table:**
| Column Name | Type |
|-------------|------|
| post_id | integer |
| user_id | integer |
| likes | integer |
| comments | integer |
| post_date | date |

**users Table:**
| Column Name | Type |
|-------------|------|
| user_id | integer |
| username | varchar |
| followers | integer |

**posts Example Input:**
| post_id | user_id | likes | comments | post_date |
|---------|---------|-------|----------|-----------|
| 1 | 123 | 500 | 25 | 2023-01-01 |
| 2 | 123 | 300 | 15 | 2023-01-02 |
| 3 | 234 | 800 | 40 | 2023-01-01 |

**users Example Input:**
| user_id | username | followers |
|---------|----------|-----------|
| 123 | john_doe | 5000 |
| 234 | jane_smith | 1200 |

**Example Output:**
| user_id | engagement_rate |
|---------|----------------|
| 123 | 16.80 |
| 234 | 70.00 |

**Explanation:**
User 123: (500+25+300+15) / 5000 × 100 = 16.80%
User 234: (800+40) / 1200 × 100 = 70.00%"""
        },
        10: {
            "title": "Zoom - Meeting Duration Analysis", 
            "description": """Given a table of Zoom meetings, find the average meeting duration for each day of the week.

Write a query to find the average meeting duration for each day of the week. Output day name and average duration in minutes rounded to 1 decimal place.

**Notes:**
- Only include meetings that actually started (status = 'completed')
- Sort by average duration descending

**meetings Table:**
| Column Name | Type |
|-------------|------|
| meeting_id | integer |
| start_time | timestamp |
| duration_minutes | integer |
| status | varchar |

**meetings Example Input:**
| meeting_id | start_time | duration_minutes | status |
|-----------|------------|------------------|--------|
| 1 | 2023-01-02 09:00:00 | 45 | completed |
| 2 | 2023-01-02 14:00:00 | 30 | completed |
| 3 | 2023-01-03 10:00:00 | 60 | completed |
| 4 | 2023-01-04 11:00:00 | 25 | cancelled |

**Example Output:**
| day_name | avg_duration |
|----------|-------------|
| Tuesday | 60.0 |
| Monday | 37.5 |

**Explanation:**
Monday (2023-01-02): (45 + 30) / 2 = 37.5 minutes average
Tuesday (2023-01-03): 60 / 1 = 60.0 minutes average
Wednesday meeting was cancelled so excluded"""
        },
        11: {
            "title": "DoorDash - Restaurant Performance Metrics",
            "description": """Given a table of restaurant orders, calculate performance metrics for each restaurant.

Write a query to calculate performance metrics for each restaurant. Output restaurant ID, total orders, average rating, and revenue per order.

**Requirements:**
- Only include restaurants with at least 50 orders
- Round average rating to 1 decimal place and revenue per order to 2 decimal places  
- Sort by total orders descending

**orders Table:**
| Column Name | Type |
|-------------|------|
| order_id | integer |
| restaurant_id | integer |
| order_amount | decimal |
| rating | integer |
| order_date | date |

**orders Example Input:**
| order_id | restaurant_id | order_amount | rating | order_date |
|---------|---------------|--------------|--------|------------|
| 1 | 101 | 25.50 | 5 | 2023-01-01 |
| 2 | 101 | 18.75 | 4 | 2023-01-02 |
| 3 | 101 | 32.00 | 5 | 2023-01-03 |
| 4 | 102 | 15.25 | 3 | 2023-01-01 |

**Example Output:**
| restaurant_id | total_orders | avg_rating | revenue_per_order |
|---------------|--------------|------------|-------------------|
| 101 | 52 | 4.5 | 28.50 |

**Explanation:**
Restaurant 101 has 52 orders (meets minimum), average rating 4.5, average revenue $28.50 per order
Restaurant 102 has only 30 orders (below minimum) so excluded"""
        },
        17: {
            "title": "Tesla - Manufacturing Defect Analysis",
            "description": """Given a table of Tesla production data, identify production lines where the defect rate increased by more than 20% compared to the previous shift.

Write a query to identify production lines where the defect rate increased by more than 20% compared to the previous shift, and calculate the rolling 7-shift average defect rate.

**Requirements:**
- Compare each shift's defect rate to the immediately previous shift on the same production line
- Include rolling 7-shift average defect rate  
- Only show results where increase > 20%
- Sort by defect rate increase descending

**production Table:**
| Column Name | Type |
|-------------|------|
| line_id | integer |
| shift_date | date |
| shift_number | integer |
| units_produced | integer |
| defective_units | integer |

**production Example Input:**
| line_id | shift_date | shift_number | units_produced | defective_units |
|---------|------------|--------------|----------------|-----------------|
| 1 | 2023-01-01 | 1 | 1000 | 10 |
| 1 | 2023-01-01 | 2 | 1000 | 15 |
| 1 | 2023-01-01 | 3 | 1000 | 25 |
| 2 | 2023-01-01 | 1 | 800 | 8 |

**Example Output:**
| line_id | shift_date | shift_number | current_defect_rate | previous_defect_rate | defect_increase_percentage |
|---------|------------|--------------|-------------------|---------------------|---------------------------|
| 1 | 2023-01-01 | 3 | 2.50 | 1.50 | 66.67 |

**Explanation:**
Line 1, Shift 3: Defect rate increased from 1.5% to 2.5% = 66.67% increase (>20% threshold)"""
        }
    }
    
    print(f"Found {len(sql_problems)} SQL problems total")
    print(f"Updating {len(problem_updates)} SQL problems with detailed schemas...")
    
    for problem_id, update_data in problem_updates.items():
        cursor.execute("""
            UPDATE problems 
            SET description = ?
            WHERE id = ?
        """, (update_data["description"], problem_id))
        
        print(f"  ✓ Updated problem {problem_id}: {update_data['title']}")
    
    conn.commit()
    print(f"\n✅ Successfully updated {len(problem_updates)} SQL problems with detailed schemas!")
    
    # Show remaining problems that need updates
    updated_ids = set(problem_updates.keys())
    remaining_problems = [p for p in sql_problems if p[0] not in updated_ids and p[0] not in [5,6,7,8]]
    
    if remaining_problems:
        print(f"\nRemaining SQL problems that need schema updates:")
        for pid, title in remaining_problems:
            print(f"  - Problem {pid}: {title}")
    
    conn.close()

if __name__ == "__main__":
    update_all_sql_problems()