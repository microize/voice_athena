"""Database configuration and initialization"""
import aiosqlite
import json
from datetime import datetime
from athena.core.config import DB_PATH

async def seed_sample_problems(db):
    """Seed the database with sample LeetCode-style problems"""
    sample_problems = [
        {
            "title": "Two Sum",
            "description": """Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.""",
            "examples": [
                {
                    "input": "nums = [2,7,11,15], target = 9",
                    "output": "[0,1]",
                    "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                },
                {
                    "input": "nums = [3,2,4], target = 6",
                    "output": "[1,2]",
                    "explanation": "Because nums[1] + nums[2] == 6, we return [1, 2]."
                }
            ],
            "constraints": [
                "2 <= nums.length <= 10^4",
                "-10^9 <= nums[i] <= 10^9",
                "-10^9 <= target <= 10^9",
                "Only one valid answer exists."
            ],
            "difficulty": "Easy",
            "category": "Array",
            "tags": ["Array", "Hash Table"],
            "test_cases": {
                "test1": {"input": "[2,7,11,15]\n9", "expected": "[0,1]"},
                "test2": {"input": "[3,2,4]\n6", "expected": "[1,2]"},
                "test3": {"input": "[3,3]\n6", "expected": "[0,1]"}
            },
            "solution_template": {
                "python": "def two_sum(nums, target):\n    # Write your code here\n    pass\n\n# Test code\ninput_line = input().strip()\nnums = eval(input_line)\ntarget = int(input())\nresult = two_sum(nums, target)\nprint(result)",
                "javascript": "function twoSum(nums, target) {\n    // Write your code here\n    return [];\n}\n\n// Test code\nconst readline = require('readline');\nconst rl = readline.createInterface({input: process.stdin});\nlet lines = [];\nrl.on('line', (line) => lines.push(line));\nrl.on('close', () => {\n    const nums = JSON.parse(lines[0]);\n    const target = parseInt(lines[1]);\n    console.log(JSON.stringify(twoSum(nums, target)));\n});",
                "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[0];\n    }\n}\n\n// Test code\nimport java.util.*;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String[] numsStr = sc.nextLine().split(\" \");\n        int[] nums = new int[numsStr.length];\n        for (int i = 0; i < numsStr.length; i++) {\n            nums[i] = Integer.parseInt(numsStr[i]);\n        }\n        int target = sc.nextInt();\n        Solution sol = new Solution();\n        int[] result = sol.twoSum(nums, target);\n        System.out.println(Arrays.toString(result));\n    }\n}",
                "cpp": "#include <vector>\n#include <iostream>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n        return {};\n    }\n};\n\n// Test code\nint main() {\n    // Implementation for reading input and testing\n    return 0;\n}",
                "csharp": "using System;\nusing System.Linq;\n\npublic class Solution {\n    public int[] TwoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[0];\n    }\n}\n\n// Test code\npublic class Program {\n    public static void Main() {\n        int[] nums = Console.ReadLine().Split(' ').Select(int.Parse).ToArray();\n        int target = int.Parse(Console.ReadLine());\n        Solution sol = new Solution();\n        int[] result = sol.TwoSum(nums, target);\n        Console.WriteLine($\"[{result[0]},{result[1]}]\");\n    }\n}"
            }
        }
        # Add more problems as needed
    ]
    
    for problem in sample_problems:
        await db.execute("""
            INSERT OR REPLACE INTO problems 
            (title, description, examples, constraints, difficulty, category, tags, test_cases, solution_template, acceptance_rate, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            problem["title"],
            problem["description"],
            json.dumps(problem["examples"]),
            json.dumps(problem["constraints"]),
            problem["difficulty"],
            problem["category"],
            json.dumps(problem["tags"]),
            json.dumps(problem["test_cases"]),
            json.dumps(problem["solution_template"]),
            85.5,  # Default acceptance rate
            datetime.now().isoformat()
        ))
    
    await db.commit()

async def init_database():
    """Initialize the database with required tables"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Create problems table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                examples TEXT,
                constraints TEXT,
                difficulty TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT,
                test_cases TEXT NOT NULL,
                solution_template TEXT,
                acceptance_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create interview sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                employee_id TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                overall_score REAL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create interview questions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                category TEXT,
                difficulty TEXT,
                asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_text TEXT,
                score REAL,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
            )
        """)
        
        # Create interview activities table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
            )
        """)
        
        # Create employees table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                department TEXT,
                position TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create other tables as needed
        await db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                problem_id INTEGER NOT NULL,
                language_id INTEGER NOT NULL,
                source_code TEXT NOT NULL,
                status TEXT NOT NULL,
                runtime REAL,
                memory_usage INTEGER,
                judge0_token TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id),
                FOREIGN KEY (user_id) REFERENCES employees (id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id TEXT PRIMARY KEY,
                problems_solved INTEGER DEFAULT 0,
                easy_solved INTEGER DEFAULT 0,
                medium_solved INTEGER DEFAULT 0,
                hard_solved INTEGER DEFAULT 0,
                total_submissions INTEGER DEFAULT 0,
                last_solved_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES employees (id)
            )
        """)
        
        await db.commit()
        await seed_sample_problems(db)