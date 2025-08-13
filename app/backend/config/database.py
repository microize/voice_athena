"""Database configuration and connection management."""

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiosqlite

from .settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Get database connection context manager."""
    async with aiosqlite.connect(settings.DB_PATH) as db:
        yield db


async def init_database():
    """Initialize the SQLite database with required tables."""
    async with get_db() as db:
        # Create employees table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT,
                role TEXT
            )
        """)
        
        # Create interview_sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                overall_score REAL
            )
        """)
        
        # Create interview_questions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                question_text TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (id)
            )
        """)
        
        # Create interview_responses table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                question_id INTEGER,
                response_text TEXT,
                score REAL NOT NULL,
                feedback TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (id),
                FOREIGN KEY (question_id) REFERENCES interview_questions (id)
            )
        """)
        
        # Create session_reports table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS session_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER UNIQUE,
                strengths TEXT,
                weaknesses TEXT,
                recommendations TEXT,
                overall_assessment TEXT,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (id)
            )
        """)
        
        # Create problems table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                examples TEXT, -- JSON array of examples with input/output/explanation
                constraints TEXT, -- JSON array of constraints
                difficulty TEXT CHECK(difficulty IN ('Easy', 'Medium', 'Hard')),
                category TEXT NOT NULL,
                tags TEXT, -- JSON array of tags
                test_cases TEXT NOT NULL, -- JSON array of test cases
                solution_template TEXT, -- JSON object with templates per language
                acceptance_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create submissions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                problem_id INTEGER NOT NULL,
                language_id INTEGER NOT NULL, -- Judge0 language ID
                source_code TEXT NOT NULL,
                status TEXT NOT NULL, -- 'Accepted', 'Wrong Answer', 'Time Limit Exceeded', etc.
                runtime REAL,
                memory_usage INTEGER,
                judge0_token TEXT, -- For async status checking
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id),
                FOREIGN KEY (user_id) REFERENCES employees (id)
            )
        """)
        
        # Create user_progress table
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
        
        # Seed sample problems if table is empty
        cursor = await db.execute("SELECT COUNT(*) FROM problems")
        count_result = await cursor.fetchone()
        if count_result[0] == 0:
            await seed_sample_problems(db)
    
    logger.info("Database initialized")


async def seed_sample_problems(db: aiosqlite.Connection):
    """Seed the database with sample LeetCode-style problems."""
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
                    "explanation": "Because nums[0] + nums[1] = 2 + 7 = 9, we return [0, 1]."
                },
                {
                    "input": "nums = [3,2,4], target = 6",
                    "output": "[1,2]",
                    "explanation": "Because nums[1] + nums[2] = 2 + 4 = 6, we return [1, 2]."
                },
                {
                    "input": "nums = [3,3], target = 6",
                    "output": "[0,1]",
                    "explanation": "Because nums[0] + nums[1] = 3 + 3 = 6, we return [0, 1]."
                }
            ],
            "constraints": [
                "2 ≤ nums.length ≤ 10^4",
                "-10^9 ≤ nums[i] ≤ 10^9",
                "-10^9 ≤ target ≤ 10^9",
                "Only one valid answer exists."
            ],
            "difficulty": "Easy",
            "category": "Array",
            "tags": ["Array", "Hash Table"],
            "test_cases": [
                {"input": "[2,7,11,15]\n9", "expected_output": "[0,1]"},
                {"input": "[3,2,4]\n6", "expected_output": "[1,2]"},
                {"input": "[3,3]\n6", "expected_output": "[0,1]"}
            ],
            "solution_template": {
                "python": "def twoSum(nums, target):\n    \"\"\"\n    :type nums: List[int]\n    :type target: int\n    :rtype: List[int]\n    \"\"\"\n    # Write your code here\n    pass\n\n# Test\nnums = list(map(int, input().split()))\ntarget = int(input())\nresult = twoSum(nums, target)\nprint(result)",
                "javascript": "/**\n * @param {number[]} nums\n * @param {number} target\n * @return {number[]}\n */\nvar twoSum = function(nums, target) {\n    // Write your code here\n};\n\n// Test\nconst readline = require('readline');\nconst rl = readline.createInterface({input: process.stdin});\nlet input = [];\nrl.on('line', (line) => {\n    input.push(line);\n    if (input.length === 2) {\n        const nums = input[0].split(' ').map(Number);\n        const target = parseInt(input[1]);\n        console.log(twoSum(nums, target));\n        rl.close();\n    }\n});",
                "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[0];\n    }\n}\n\n// Test code\nimport java.util.*;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String[] numsStr = sc.nextLine().split(\" \");\n        int[] nums = new int[numsStr.length];\n        for (int i = 0; i < numsStr.length; i++) {\n            nums[i] = Integer.parseInt(numsStr[i]);\n        }\n        int target = sc.nextInt();\n        Solution sol = new Solution();\n        int[] result = sol.twoSum(nums, target);\n        System.out.println(Arrays.toString(result));\n    }\n}"
            },
            "acceptance_rate": 54.1
        },
        {
            "title": "Valid Parentheses",
            "description": """Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.""",
            "examples": [
                {
                    "input": "s = \"()\"",
                    "output": "true",
                    "explanation": "The string contains one pair of valid parentheses."
                },
                {
                    "input": "s = \"()[]{}\"",
                    "output": "true",
                    "explanation": "The string contains three pairs of valid brackets, all properly closed."
                },
                {
                    "input": "s = \"(]\"",
                    "output": "false",
                    "explanation": "The opening parenthesis is closed by a square bracket, which is invalid."
                }
            ],
            "constraints": [
                "1 ≤ s.length ≤ 10^4",
                "s consists of parentheses only '()[]{}'."
            ],
            "difficulty": "Easy",
            "category": "String",
            "tags": ["String", "Stack"],
            "test_cases": [
                {"input": "()", "expected_output": "true"},
                {"input": "()[]{}", "expected_output": "true"},
                {"input": "(]", "expected_output": "false"},
                {"input": "([)]", "expected_output": "false"},
                {"input": "{[]}", "expected_output": "true"}
            ],
            "solution_template": {
                "python": "def isValid(s):\n    \"\"\"\n    :type s: str\n    :rtype: bool\n    \"\"\"\n    # Write your code here\n    pass\n\n# Test\ns = input().strip()\nresult = isValid(s)\nprint(str(result).lower())"
            },
            "acceptance_rate": 42.3
        }
    ]
    
    for problem in sample_problems:
        await db.execute("""
            INSERT INTO problems 
            (title, description, examples, constraints, difficulty, category, tags, test_cases, solution_template, acceptance_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            problem["title"],
            problem["description"],
            json.dumps(problem.get("examples", [])),
            json.dumps(problem.get("constraints", [])),
            problem["difficulty"],
            problem["category"],
            json.dumps(problem["tags"]),
            json.dumps(problem["test_cases"]),
            json.dumps(problem["solution_template"]),
            problem["acceptance_rate"]
        ))
    
    await db.commit()
    logger.info("Sample problems seeded successfully")