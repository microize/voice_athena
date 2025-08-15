#!/usr/bin/env python3
"""
Final update for remaining SQL problems with comprehensive schemas
"""

import sqlite3
import json

def final_sql_schema_update():
    conn = sqlite3.connect('../data/interview_sessions.db')
    cursor = conn.cursor()
    
    # Final batch of SQL problems with comprehensive schemas
    final_updates = {
        12: {
            "description": """Given a table of sales leads and their progression through stages, analyze the lead conversion funnel.

Write a query to analyze the lead conversion funnel by showing conversion rates at each stage. Output stage name and conversion rate as percentage rounded to 2 decimal places.

**Stages:** lead → opportunity → customer
**Note:** Conversion rate = (Count of current stage / Count of previous stage) × 100

**leads Table:**
| Column Name | Type |
|-------------|------|
| lead_id | integer |
| stage | varchar |
| created_date | date |

**leads Example Input:**
| lead_id | stage | created_date |
|---------|-------|--------------|
| 1 | lead | 2023-01-01 |
| 2 | lead | 2023-01-02 |
| 3 | opportunity | 2023-01-03 |
| 4 | customer | 2023-01-04 |

**Example Output:**
| conversion_type | conversion_rate |
|----------------|-----------------|
| lead_to_opportunity | 50.00 |
| opportunity_to_customer | 100.00 |

**Explanation:**
2 leads total, 1 became opportunity = 50% lead-to-opportunity conversion
1 opportunity total, 1 became customer = 100% opportunity-to-customer conversion"""
        },
        13: {
            "description": """Given a table of Pinterest pins with engagement metrics, find the top 3 categories with highest average engagement per pin.

Write a query to find the top 3 pin categories with highest average engagement per pin. Output category and average engagement rounded to 1 decimal place.

**Definition:**
- Engagement = saves + likes + clicks
- Only include categories with at least 100 pins

**pins Table:**
| Column Name | Type |
|-------------|------|
| pin_id | integer |
| category | varchar |
| saves | integer |
| likes | integer |
| clicks | integer |

**pins Example Input:**
| pin_id | category | saves | likes | clicks |
|--------|----------|-------|-------|--------|
| 1 | Fashion | 25 | 150 | 75 |
| 2 | Food | 40 | 200 | 100 |
| 3 | Fashion | 30 | 180 | 90 |
| 4 | Food | 35 | 160 | 80 |

**Example Output:**
| category | avg_engagement |
|----------|---------------|
| Food | 287.5 |
| Fashion | 275.0 |

**Explanation:**
Fashion: ((25+150+75) + (30+180+90)) / 2 = 275.0 average engagement
Food: ((40+200+100) + (35+160+80)) / 2 = 287.5 average engagement"""
        },
        14: {
            "description": """Given a table of Slack messages, identify peak activity hours for each channel.

Write a query to identify peak activity hours for each channel. Output channel ID and the hour (0-23) with most messages.

**Requirements:**
- Use message timestamp to extract hour
- In case of ties, show the earliest hour  
- Only include channels with at least 200 messages

**messages Table:**
| Column Name | Type |
|-------------|------|
| message_id | integer |
| channel_id | integer |
| message_timestamp | timestamp |
| user_id | integer |

**messages Example Input:**
| message_id | channel_id | message_timestamp | user_id |
|-----------|------------|-------------------|---------|
| 1 | 101 | 2023-01-01 09:30:00 | 1 |
| 2 | 101 | 2023-01-01 09:45:00 | 2 |
| 3 | 101 | 2023-01-01 14:15:00 | 1 |
| 4 | 102 | 2023-01-01 10:20:00 | 3 |

**Example Output:**
| channel_id | peak_hour |
|-----------|-----------|
| 101 | 9 |

**Explanation:**
Channel 101: Hour 9 has 2 messages, Hour 14 has 1 message. Peak is hour 9.
Channel 102 excluded (less than 200 total messages)"""
        },
        15: {
            "description": """Given a table of monthly sales data, calculate month-over-month sales growth for each store.

Write a query to calculate month-over-month sales growth for each store. Output store ID, month, current month sales, previous month sales, and growth percentage.

**Notes:**
- Growth percentage = (Current - Previous) / Previous × 100
- Round growth percentage to 2 decimal places
- Show results for 2023 only

**sales Table:**
| Column Name | Type |
|-------------|------|
| sale_id | integer |
| store_id | integer |
| sale_date | date |
| sale_amount | decimal |

**sales Example Input:**
| sale_id | store_id | sale_date | sale_amount |
|---------|----------|-----------|-------------|
| 1 | 101 | 2023-01-15 | 1000.00 |
| 2 | 101 | 2023-01-20 | 1500.00 |
| 3 | 101 | 2023-02-10 | 1800.00 |
| 4 | 101 | 2023-02-25 | 2200.00 |

**Example Output:**
| store_id | month | current_sales | previous_sales | growth_percentage |
|----------|-------|---------------|----------------|-------------------|
| 101 | 2023-02-01 | 4000.00 | 2500.00 | 60.00 |

**Explanation:**
Store 101: January total = $2,500, February total = $4,000
Growth = (4000 - 2500) / 2500 × 100 = 60.00%"""
        },
        16: {
            "description": """Given tables of Discord server members and their activity, calculate 30-day member retention rate for each server.

Write a query to calculate 30-day member retention rate for each server. Output server ID and retention rate as percentage rounded to 2 decimal places.

**Definition:**
- Retention rate = (Members still active after 30 days / Total new members) × 100
- Consider a member active if they sent at least 1 message in days 30-35 after joining

**members Table:**
| Column Name | Type |
|-------------|------|
| user_id | integer |
| server_id | integer |
| join_date | date |

**activity Table:**
| Column Name | Type |
|-------------|------|
| user_id | integer |
| server_id | integer |
| activity_date | date |
| message_count | integer |

**members Example Input:**
| user_id | server_id | join_date |
|---------|-----------|-----------|
| 1 | 101 | 2023-01-01 |
| 2 | 101 | 2023-01-02 |
| 3 | 101 | 2023-01-03 |

**activity Example Input:**
| user_id | server_id | activity_date | message_count |
|---------|-----------|---------------|---------------|
| 1 | 101 | 2023-02-02 | 5 |
| 2 | 101 | 2023-02-03 | 2 |

**Example Output:**
| server_id | retention_rate |
|-----------|---------------|
| 101 | 66.67 |

**Explanation:**
Server 101: 3 new members, 2 were active 30+ days later = 66.67% retention"""
        }
    }
    
    print(f"Applying final schema updates to {len(final_updates)} SQL problems...")
    
    for problem_id, update_data in final_updates.items():
        cursor.execute("""
            UPDATE problems 
            SET description = ?
            WHERE id = ?
        """, (update_data["description"], problem_id))
        
        # Get the title for confirmation
        cursor.execute("SELECT title FROM problems WHERE id = ?", (problem_id,))
        title = cursor.fetchone()[0]
        print(f"  ✓ Updated problem {problem_id}: {title}")
    
    conn.commit()
    print(f"\n✅ Final schema updates completed for {len(final_updates)} problems!")
    
    # Show final status
    cursor.execute("SELECT COUNT(*) FROM problems WHERE category = 'SQL'")
    total_sql = cursor.fetchone()[0]
    updated_count = 8 + len(final_updates)  # Previous + current updates
    
    print(f"\nSchema Update Status:")
    print(f"  - Total SQL problems: {total_sql}")
    print(f"  - Updated with schemas: {updated_count}")
    print(f"  - Remaining: {total_sql - updated_count}")
    
    conn.close()

if __name__ == "__main__":
    final_sql_schema_update()