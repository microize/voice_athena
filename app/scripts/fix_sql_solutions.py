#!/usr/bin/env python3
"""
Script to fix SQL problems by moving solutions to the solutions field
and updating templates to provide proper starter code
"""

import sqlite3
import json
from datetime import datetime

def fix_sql_solutions():
    conn = sqlite3.connect('../data/interview_sessions.db')
    cursor = conn.cursor()
    
    # Get all SQL problems
    cursor.execute("SELECT id, title, solution_template FROM problems WHERE category = 'SQL'")
    sql_problems = cursor.fetchall()
    
    print(f"Found {len(sql_problems)} SQL problems to fix")
    
    for problem_id, title, solution_template_str in sql_problems:
        print(f"Fixing problem {problem_id}: {title}")
        
        # Parse the current solution_template which contains the actual solution
        try:
            current_template = json.loads(solution_template_str)
            actual_solution = current_template.get('sql', '')
            
            # Create proper solution entry
            solutions = {
                'sql': actual_solution
            }
            
            # Create proper starter template
            # This should be a basic template that users can start with
            template = {
                'sql': '-- Write your SQL query here\n-- Sample structure:\nSELECT \n    \nFROM \n    \nWHERE \n    '
            }
            
            # Update the database
            cursor.execute("""
                UPDATE problems 
                SET solution_template = ?, solutions = ?
                WHERE id = ?
            """, (json.dumps(template), json.dumps(solutions), problem_id))
            
            print(f"  ✓ Updated problem {problem_id}")
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Error parsing JSON for problem {problem_id}: {e}")
            continue
    
    conn.commit()
    print(f"\n✅ Successfully updated {len(sql_problems)} SQL problems!")
    
    # Verify the changes
    print("\nVerifying updates...")
    cursor.execute("SELECT id, title, solutions FROM problems WHERE category = 'SQL' LIMIT 3")
    updated_problems = cursor.fetchall()
    
    for problem_id, title, solutions_str in updated_problems:
        if solutions_str:
            try:
                solutions = json.loads(solutions_str)
                sql_solution = solutions.get('sql', '')
                print(f"Problem {problem_id}: {title}")
                print(f"  Solution preview: {sql_solution[:100]}...")
                print()
            except json.JSONDecodeError:
                print(f"Problem {problem_id}: Invalid solutions JSON")
    
    conn.close()

if __name__ == "__main__":
    fix_sql_solutions()