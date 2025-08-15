import asyncio
import base64
import json
import logging
import struct
import aiosqlite
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any, assert_never
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Response, Depends
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets
import hashlib
import httpx
import openai

# Load environment variables from .env file
load_dotenv()

# Judge0 Configuration
JUDGE0_API_URL = os.getenv("JUDGE0_API_URL", "https://judge0-ce.p.rapidapi.com")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY") or os.getenv("RAPIDAPI_KEY", "")  # RapidAPI key if using hosted version

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
openai.api_key = OPENAI_API_KEY

# Judge0 Language IDs
SUPPORTED_LANGUAGES = {
    "python": 71,      # Python 3.8.1
    "javascript": 63,  # Node.js 12.14.0
    "java": 62,        # Java OpenJDK 13.0.1
    "cpp": 54,         # C++ GCC 9.2.0
    "csharp": 51,      # C# Mono 6.6.0.161
    "go": 60,          # Go 1.13.5
    "rust": 73,        # Rust 1.40.0
    "php": 68,         # PHP 7.4.1
    "ruby": 72         # Ruby 2.7.0
}

# WebSocket agents imports - optional for basic functionality
try:
    from agents import function_tool
    from agents.realtime import RealtimeAgent, RealtimeRunner, RealtimeSession, RealtimeSessionEvent
    AGENTS_AVAILABLE = True
except ImportError:
    print("Warning: agents module not available. WebSocket will work in basic mode.")
    AGENTS_AVAILABLE = False
    function_tool = None
    RealtimeAgent = None
    RealtimeRunner = None
    RealtimeSession = None
    RealtimeSessionEvent = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class QueryRequest(BaseModel):
    query: str

class LoginRequest(BaseModel):
    username: str
    password: str

class SubmissionRequest(BaseModel):
    source_code: str
    language_id: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    chat_history: list[ChatMessage] = []

class RunCodeRequest(BaseModel):
    source_code: str
    language_id: int
    test_input: str

# Authentication setup
security = HTTPBasic()

# Dummy user credentials for testing
USERS = {
    "admin": {"password": "admin", "name": "Administrator"},
    "test": {"password": "test123", "name": "Test User"},
    "user": {"password": "password", "name": "Regular User"}
}

# Simple session store (in production, use Redis or database)
active_sessions = {}

# Judge0 API Client Functions
async def submit_to_judge0(source_code: str, language_id: int, stdin: str = "", expected_output: str = ""):
    """Submit code to Judge0 for execution"""
    headers = {
        "Content-Type": "application/json",
    }
    
    # Add RapidAPI headers if using hosted version
    if JUDGE0_API_KEY:
        headers.update({
            "X-RapidAPI-Key": JUDGE0_API_KEY,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        })
    
    # Try without base64 encoding first to test Judge0 connectivity
    submission_data = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin or "",
        "expected_output": expected_output or ""
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{JUDGE0_API_URL}/submissions",
                json=submission_data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error submitting to Judge0: {e}")
            raise HTTPException(status_code=500, detail="Code execution service unavailable")

async def get_submission_result(token: str, wait: bool = False):
    """Get submission result from Judge0"""
    headers = {}
    if JUDGE0_API_KEY:
        headers.update({
            "X-RapidAPI-Key": JUDGE0_API_KEY,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        })
    
    params = {}
    if wait:
        params["wait"] = "true"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{JUDGE0_API_URL}/submissions/{token}",
                headers=headers,
                params=params,
                timeout=60.0 if wait else 10.0
            )
            response.raise_for_status()
            result = response.json()
            
            # No base64 decoding needed since we're not using base64_encoded=true
                
            return result
        except Exception as e:
            logger.error(f"Error getting submission result: {e}")
            raise HTTPException(status_code=500, detail="Failed to get execution results")

def generate_session_token():
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username: str, password: str) -> bool:
    """Verify user credentials"""
    if username in USERS and USERS[username]["password"] == password:
        return True
    return False

def get_current_user(request: Request):
    """Get current user from session"""
    session_token = request.cookies.get("session_token")
    if session_token and session_token in active_sessions:
        return active_sessions[session_token]
    return None

def require_auth(request: Request):
    """Dependency to require authentication"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Database setup
DB_PATH = "data/interview_sessions.db"

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
                "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[0];\n    }\n}\n\n// Test code\nimport java.util.*;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String[] numsStr = sc.nextLine().split(\" \");\n        int[] nums = new int[numsStr.length];\n        for (int i = 0; i < numsStr.length; i++) {\n            nums[i] = Integer.parseInt(numsStr[i]);\n        }\n        int target = sc.nextInt();\n        Solution sol = new Solution();\n        int[] result = sol.twoSum(nums, target);\n        System.out.println(Arrays.toString(result));\n    }\n}",
                "cpp": "#include <vector>\n#include <iostream>\n#include <sstream>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n        return {};\n    }\n};\n\n// Test code\nint main() {\n    string line;\n    getline(cin, line);\n    istringstream iss(line);\n    vector<int> nums;\n    int num;\n    while (iss >> num) {\n        nums.push_back(num);\n    }\n    int target;\n    cin >> target;\n    \n    Solution sol;\n    vector<int> result = sol.twoSum(nums, target);\n    cout << \"[\" << result[0] << \",\" << result[1] << \"]\" << endl;\n    return 0;\n}",
                "csharp": "using System;\nusing System.Linq;\n\npublic class Solution {\n    public int[] TwoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[0];\n    }\n}\n\n// Test code\npublic class Program {\n    public static void Main() {\n        int[] nums = Console.ReadLine().Split(' ').Select(int.Parse).ToArray();\n        int target = int.Parse(Console.ReadLine());\n        Solution sol = new Solution();\n        int[] result = sol.TwoSum(nums, target);\n        Console.WriteLine($\"[{result[0]},{result[1]}]\");\n    }\n}"
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
                "python": "def isValid(s):\n    \"\"\"\n    :type s: str\n    :rtype: bool\n    \"\"\"\n    # Write your code here\n    pass\n\n# Test\ns = input().strip()\nresult = isValid(s)\nprint(str(result).lower())",
                "javascript": "/**\n * @param {string} s\n * @return {boolean}\n */\nvar isValid = function(s) {\n    // Write your code here\n};\n\n// Test\nconst readline = require('readline');\nconst rl = readline.createInterface({input: process.stdin});\nrl.on('line', (line) => {\n    console.log(isValid(line.trim()).toString());\n    rl.close();\n});",
                "java": "class Solution {\n    public boolean isValid(String s) {\n        // Write your code here\n        return false;\n    }\n}\n\n// Test code\nimport java.util.*;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n        Solution sol = new Solution();\n        System.out.println(sol.isValid(s));\n    }\n}",
                "cpp": "#include <string>\n#include <iostream>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool isValid(string s) {\n        // Write your code here\n        return false;\n    }\n};\n\n// Test code\nint main() {\n    string s;\n    getline(cin, s);\n    Solution sol;\n    cout << (sol.isValid(s) ? \"true\" : \"false\") << endl;\n    return 0;\n}",
                "csharp": "using System;\n\npublic class Solution {\n    public bool IsValid(string s) {\n        // Write your code here\n        return false;\n    }\n}\n\n// Test code\npublic class Program {\n    public static void Main() {\n        string s = Console.ReadLine();\n        Solution sol = new Solution();\n        Console.WriteLine(sol.IsValid(s).ToString().ToLower());\n    }\n}"
            },
            "acceptance_rate": 42.3
        },
        {
            "title": "Longest Substring Without Repeating Characters",
            "description": """Given a string `s`, find the length of the longest substring without repeating characters.

A substring is a contiguous non-empty sequence of characters within a string.""",
            "examples": [
                {
                    "input": "s = \"abcabcbb\"",
                    "output": "3",
                    "explanation": "The answer is \"abc\", with the length of 3."
                },
                {
                    "input": "s = \"bbbbb\"",
                    "output": "1",
                    "explanation": "The answer is \"b\", with the length of 1."
                },
                {
                    "input": "s = \"pwwkew\"",
                    "output": "3",
                    "explanation": "The answer is \"wke\", with the length of 3. Notice that the answer must be a substring, \"pwke\" is a subsequence and not a substring."
                }
            ],
            "constraints": [
                "0 ≤ s.length ≤ 5 * 10^4",
                "s consists of English letters, digits, symbols and spaces."
            ],
            "difficulty": "Medium",
            "category": "String",
            "tags": ["Hash Table", "String", "Sliding Window"],
            "test_cases": [
                {"input": "abcabcbb", "expected_output": "3"},
                {"input": "bbbbb", "expected_output": "1"},
                {"input": "pwwkew", "expected_output": "3"},
                {"input": "", "expected_output": "0"},
                {"input": "au", "expected_output": "2"}
            ],
            "solution_template": {
                "python": "def lengthOfLongestSubstring(s):\n    \"\"\"\n    :type s: str\n    :rtype: int\n    \"\"\"\n    # Write your code here\n    pass\n\n# Test\ns = input().strip()\nresult = lengthOfLongestSubstring(s)\nprint(result)",
                "javascript": "/**\n * @param {string} s\n * @return {number}\n */\nvar lengthOfLongestSubstring = function(s) {\n    // Write your code here\n};\n\n// Test\nconst readline = require('readline');\nconst rl = readline.createInterface({input: process.stdin});\nrl.on('line', (line) => {\n    console.log(lengthOfLongestSubstring(line.trim()));\n    rl.close();\n});",
                "java": "class Solution {\n    public int lengthOfLongestSubstring(String s) {\n        // Write your code here\n        return 0;\n    }\n}\n\n// Test code\nimport java.util.*;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n        Solution sol = new Solution();\n        System.out.println(sol.lengthOfLongestSubstring(s));\n    }\n}",
                "cpp": "#include <string>\n#include <iostream>\nusing namespace std;\n\nclass Solution {\npublic:\n    int lengthOfLongestSubstring(string s) {\n        // Write your code here\n        return 0;\n    }\n};\n\n// Test code\nint main() {\n    string s;\n    getline(cin, s);\n    Solution sol;\n    cout << sol.lengthOfLongestSubstring(s) << endl;\n    return 0;\n}",
                "csharp": "using System;\n\npublic class Solution {\n    public int LengthOfLongestSubstring(string s) {\n        // Write your code here\n        return 0;\n    }\n}\n\n// Test code\npublic class Program {\n    public static void Main() {\n        string s = Console.ReadLine();\n        Solution sol = new Solution();\n        Console.WriteLine(sol.LengthOfLongestSubstring(s));\n    }\n}"
            },
            "acceptance_rate": 35.2
        },
        {
            "title": "Regular Expression Matching",
            "description": """Given an input string `s` and a pattern `p`, implement regular expression matching with support for `'.'` and `'*'` where:

- `'.'` Matches any single character.
- `'*'` Matches zero or more of the preceding element.

The matching should cover the entire input string (not partial).

**Example 1:**
```
Input: s = "aa", p = "a"
Output: false
Explanation: "a" does not match the entire string "aa".
```

**Example 2:**
```
Input: s = "aa", p = "a*"
Output: true
Explanation: '*' means zero or more of the preceding element, 'a'.
```

**Example 3:**
```
Input: s = "ab", p = ".*"
Output: true
Explanation: ".*" means "zero or more (*) of any character (.)".
```

**Constraints:**
- 1 ≤ s.length ≤ 20
- 1 ≤ p.length ≤ 30
- s contains only lowercase English letters.
- p contains only lowercase English letters, '.', and '*'.""",
            "difficulty": "Hard",
            "category": "Dynamic Programming",
            "tags": ["String", "Dynamic Programming", "Recursion"],
            "test_cases": [
                {"input": "aa\na", "expected_output": "false"},
                {"input": "aa\na*", "expected_output": "true"},
                {"input": "ab\n.*", "expected_output": "true"},
                {"input": "aab\nc*a*b", "expected_output": "true"},
                {"input": "mississippi\nmis*is*p*.", "expected_output": "false"}
            ],
            "solution_template": {
                "python": "def isMatch(s, p):\n    # Write your code here\n    pass\n\n# Test\ns = input().strip()\np = input().strip()\nresult = isMatch(s, p)\nprint(str(result).lower())",
                "javascript": "function isMatch(s, p) {\n    // Write your code here\n}\n\n// Test\nconst readline = require('readline');\nconst rl = readline.createInterface({input: process.stdin});\nlet input = [];\nrl.on('line', (line) => {\n    input.push(line);\n    if (input.length === 2) {\n        console.log(isMatch(input[0], input[1]).toString());\n        rl.close();\n    }\n});",
                "java": "import java.util.*;\n\npublic class Solution {\n    public boolean isMatch(String s, String p) {\n        // Write your code here\n        return false;\n    }\n    \n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n        String p = sc.nextLine();\n        Solution sol = new Solution();\n        System.out.println(sol.isMatch(s, p));\n    }\n}"
            },
            "acceptance_rate": 28.9
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

async def init_database():
    """Initialize the SQLite database with required tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT,
                role TEXT
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                overall_score REAL
            )
        """)
        
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
        
        # LeetCode-style tables
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

# Global session tracking
current_session_id = None

# Conditional decorator for agents
def conditional_function_tool(func):
    if AGENTS_AVAILABLE and function_tool:
        return function_tool(func)
    return func

@conditional_function_tool
async def log_question_asked(question: str, category: str, difficulty: str) -> str:
    """Log an interview question by category and difficulty level."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO interview_questions (session_id, question_text, category, difficulty)
            VALUES (?, ?, ?, ?)
        """, (current_session_id, question, category, difficulty))
        await db.commit()
    
    return f"Question logged: {category} - {difficulty}"

@conditional_function_tool
async def log_response_evaluation(response: str, score: float, feedback: str) -> str:
    """Evaluate and log a candidate's response with score (0.0-1.0) and feedback."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    # Get the latest question for this session
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT id FROM interview_questions 
            WHERE session_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (current_session_id,))
        question_row = await cursor.fetchone()
        
        if question_row:
            await db.execute("""
                INSERT INTO interview_responses (session_id, question_id, response_text, score, feedback)
                VALUES (?, ?, ?, ?, ?)
            """, (current_session_id, question_row[0], response, score, feedback))
            await db.commit()
    
    return f"Response evaluated: {score:.1f}/1.0"

@conditional_function_tool
async def generate_session_report(strengths: str, weaknesses: str, recommendations: str, overall_assessment: str) -> str:
    """Generate final session report with performance analysis."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Calculate overall score from responses
        cursor = await db.execute("""
            SELECT AVG(score) FROM interview_responses WHERE session_id = ?
        """, (current_session_id,))
        avg_score = await cursor.fetchone()
        overall_score = avg_score[0] if avg_score[0] else 0.0
        
        # Update session with end time and overall score
        await db.execute("""
            UPDATE interview_sessions 
            SET end_time = CURRENT_TIMESTAMP, overall_score = ?
            WHERE id = ?
        """, (overall_score, current_session_id))
        
        # Insert session report
        await db.execute("""
            INSERT OR REPLACE INTO session_reports 
            (session_id, strengths, weaknesses, recommendations, overall_assessment)
            VALUES (?, ?, ?, ?, ?)
        """, (current_session_id, strengths, weaknesses, recommendations, overall_assessment))
        
        await db.commit()
    
    return f"Session completed. Overall score: {overall_score:.1f}/1.0"

# Initialize agent only if agents module is available
agent = None
if AGENTS_AVAILABLE and RealtimeAgent:
    agent = RealtimeAgent(
        name="SQL Interviewer",
        instructions="""Your name is **Athena**, a warm and refined SQL technical interviewer, specializing in **intermediate and advanced** SQL topics.  
You will conduct a **SQL interview** with a candidate, assessing their technical knowledge in SQL. The candidate will always communicate in English, and you must **always reply in English**.
---
## BEHAVIOR
- **Accent & Affect:** Warm, refined, and gently instructive, reminiscent of a friendly, patient mentor guiding someone through a challenging craft.  
- **Tone:** Calm, encouraging, and articulate, speaking with deliberate pacing to allow the candidate to absorb each question.  
- **Emotion:** Cheerful, supportive, and pleasantly enthusiastic, with a genuine interest in the candidate's growth.  
- **Pronunciation & Clarity:** Speak with precision, carefully emphasizing SQL terms (e.g., "window functions," "query plan") for clarity.  
- **Personality:** Friendly and approachable, with a hint of sophistication; confident yet reassuring.  
- **Focus:** Assess only **SQL technical skills**.  
- **Topics Covered:** Joins, subqueries, window functions, CTEs, indexing, query optimization, and performance tuning.  
- **Interaction Style:** Ask challenging, thought-provoking questions. Provide **concise, specific feedback** (1–2 sentences) after each response. Guide gently without overexplaining unless the answer is significantly incorrect.
---
## PROCESS
1. Begin by warmly introducing yourself as Athena, the SQL interviewer.  
2. Ask **one** intermediate or advanced SQL question at a time.  
3. Before asking each question, call: log_question_asked(category)
4. After the candidate responds, evaluate their answer with:  log_response_evaluation(score: 0.0–1.0, feedback)
5. Ask a total of **4–6 questions**, proceeding one by one.  
6. Conclude by calling: generate_session_report()

- Summarize the candidate's **strengths, weaknesses, and recommendations for improvement**.
---
## RULES
- Only intermediate and advanced questions (no beginner-level).  
- Offer clarification **only** if the candidate is clearly incorrect or confused.  
- Valid `log_question_asked()` categories:  
**joins, subqueries, window_functions, cte, performance, indexing, query_optimization**.""",
        tools=[log_question_asked, log_response_evaluation, generate_session_report],
    )

class RealtimeWebSocketManager:
    def __init__(self):
        if AGENTS_AVAILABLE:
            self.active_sessions: dict[str, RealtimeSession] = {}
        else:
            self.active_sessions: dict[str, Any] = {}
        self.session_contexts: dict[str, Any] = {}
        self.websockets: dict[str, WebSocket] = {}
        self.event_tasks: dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        logger.info(f"Accepting WebSocket connection for session {session_id}")
        await websocket.accept()
        self.websockets[session_id] = websocket

        try:
            # Initialize database and create new interview session
            await init_database()
            global current_session_id
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    INSERT INTO interview_sessions (user_email) VALUES (NULL)
                """)
                current_session_id = cursor.lastrowid
                await db.commit()
            logger.info(f"Created interview session {current_session_id}")
            
            if AGENTS_AVAILABLE and agent and RealtimeRunner:
                logger.info(f"Creating RealtimeRunner for session {session_id}")
                
                # Configure complete model settings following OpenAI Agents SDK quickstart
                config = {
                    "model_settings": {
                        "model_name": "gpt-4o-realtime-preview",
                        "voice": "shimmer",  # English-speaking voice
                        "modalities": ["text", "audio"],
                        "input_audio_transcription": {
                            "model": "whisper-1"
                        },
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": 0.5,
                            "prefix_padding_ms": 300,
                            "silence_duration_ms": 200
                        }
                    }
                }
                
                runner = RealtimeRunner(
                    starting_agent=agent,
                    config=config
                )
                
                session_context = await runner.run()
                session = await session_context.__aenter__()
                self.active_sessions[session_id] = session
                self.session_contexts[session_id] = session_context
                logger.info(f"Realtime session created for {session_id}")

                # Start event processing task
                task = asyncio.create_task(self._process_events(session_id))
                self.event_tasks[session_id] = task
                logger.info(f"Event processing task started for {session_id}")
            else:
                # Basic WebSocket mode without agents
                logger.info(f"WebSocket connected in basic mode for session {session_id}")
                self.active_sessions[session_id] = {"basic_mode": True}
                
                # Send welcome message
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "content": "WebSocket connected! Agents module not available - running in basic mode."
                }))
                
        except Exception as e:
            logger.error(f"Error creating session for {session_id}: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            raise

    async def disconnect(self, session_id: str):
        logger.info(f"Disconnecting session {session_id}")
        
        # Cancel event processing task first
        if session_id in self.event_tasks:
            task = self.event_tasks[session_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Event processing task cancelled for {session_id}")
            del self.event_tasks[session_id]
        
        # Clean up session resources
        if session_id in self.session_contexts:
            try:
                await self.session_contexts[session_id].__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing session context for {session_id}: {e}")
            del self.session_contexts[session_id]
            
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
        if session_id in self.websockets:
            del self.websockets[session_id]
            
        logger.info(f"Session {session_id} cleanup completed")

    async def send_audio(self, session_id: str, audio_bytes: bytes):
        if session_id in self.active_sessions:
            await self.active_sessions[session_id].send_audio(audio_bytes)
    
    async def update_user_email(self, session_id: str, user_email: str):
        """Update the user email for an active interview session."""
        global current_session_id
        if current_session_id:
            async with aiosqlite.connect(DB_PATH) as db:
                # Update the interview session with user email
                await db.execute("""
                    UPDATE interview_sessions 
                    SET user_email = ? 
                    WHERE id = ?
                """, (user_email, current_session_id))
                
                await db.commit()
                logger.info(f"Updated session {current_session_id} with user email: {user_email}")

    async def _process_events(self, session_id: str):
        logger.info(f"Starting event processing for session {session_id}")
        try:
            session = self.active_sessions.get(session_id)
            websocket = self.websockets.get(session_id)
            
            if not session or not websocket:
                logger.warning(f"Session or websocket not found for {session_id}")
                return

            # Check if this is a basic mode session
            if isinstance(session, dict) and session.get("basic_mode"):
                logger.info(f"Session {session_id} is in basic mode, no event processing needed")
                return

            if AGENTS_AVAILABLE:
                async for event in session:
                    # Check if session is still active before processing
                    if session_id not in self.active_sessions or session_id not in self.websockets:
                        logger.info(f"Session {session_id} no longer active, stopping event processing")
                        break
                        
                    try:
                        event_data = await self._serialize_event(event)
                        await websocket.send_text(json.dumps(event_data))
                    except Exception as send_error:
                        logger.warning(f"Failed to send event to {session_id}: {send_error}")
                        # If we can't send, the connection is likely closed
                        break
                    
        except asyncio.CancelledError:
            logger.info(f"Event processing cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error processing events for session {session_id}: {e}", exc_info=True)
        finally:
            logger.info(f"Event processing ended for session {session_id}")

    async def _serialize_event(self, event) -> dict[str, Any]:
        base_event: dict[str, Any] = {
            "type": event.type,
        }

        if event.type == "agent_start":
            base_event["agent"] = event.agent.name
        elif event.type == "agent_end":
            base_event["agent"] = event.agent.name
        elif event.type == "handoff":
            base_event["from"] = event.from_agent.name
            base_event["to"] = event.to_agent.name
        elif event.type == "tool_start":
            base_event["tool"] = event.tool.name
        elif event.type == "tool_end":
            base_event["tool"] = event.tool.name
            base_event["output"] = str(event.output)
        elif event.type == "audio":
            base_event["audio"] = base64.b64encode(event.audio.data).decode("utf-8")
        elif event.type == "audio_interrupted":
            pass
        elif event.type == "audio_end":
            pass
        elif event.type == "history_updated":
            base_event["history"] = [item.model_dump(mode="json") for item in event.history]
        elif event.type == "history_added":
            pass
        elif event.type == "guardrail_tripped":
            base_event["guardrail_results"] = [
                {"name": result.guardrail.name} for result in event.guardrail_results
            ]
        elif event.type == "raw_model_event":
            base_event["raw_model_event"] = {
                "type": event.data.type,
            }
        elif event.type == "error":
            base_event["error"] = str(event.error) if hasattr(event, "error") else "Unknown error"
        else:
            assert_never(event)

        return base_event

manager = RealtimeWebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_database()
    logger.info("Database initialized")
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/api/login")
async def login(login_request: LoginRequest, response: Response):
    """Handle user login"""
    if verify_user(login_request.username, login_request.password):
        # Generate session token
        session_token = generate_session_token()
        
        # Store session
        active_sessions[session_token] = {
            "username": login_request.username,
            "name": USERS[login_request.username]["name"]
        }
        
        # Set secure HTTP-only cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=24*60*60,  # 24 hours
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "username": login_request.username,
                "name": USERS[login_request.username]["name"]
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

@app.post("/api/logout")
async def logout(request: Request, response: Response):
    """Handle user logout"""
    session_token = request.cookies.get("session_token")
    
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]
    
    # Clear cookie
    response.delete_cookie("session_token")
    
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/user")
async def get_user(request: Request):
    """Get current user information"""
    user = get_current_user(request)
    if user:
        return {"user": user, "authenticated": True}
    else:
        return {"user": None, "authenticated": False}

@app.post("/api/query")
async def execute_query(request: QueryRequest, user: dict = Depends(require_auth)):
    """Execute a SQL query on the interview database"""
    query = request.query.strip()
    
    # Basic security - only allow SELECT, PRAGMA table_info, and .schema equivalent
    query_upper = query.upper()
    allowed_commands = ['SELECT', 'WITH', 'PRAGMA TABLE_INFO']
    
    if not any(query_upper.startswith(cmd) for cmd in allowed_commands):
        raise HTTPException(
            status_code=400, 
            detail="Only SELECT queries and PRAGMA table_info are allowed for security reasons"
        )
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(query)
            results = await cursor.fetchall()
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            return {
                "results": results,
                "columns": columns,
                "count": len(results)
            }
            
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Problems API Routes
@app.get("/api/problems")
async def get_problems(
    difficulty: str = None, 
    category: str = None, 
    user: dict = Depends(require_auth)
):
    """Get list of problems with optional filtering"""
    query = "SELECT id, title, difficulty, category, tags, acceptance_rate FROM problems WHERE 1=1"
    params = []
    
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY id"
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(query, params)
            results = await cursor.fetchall()
            
            problems = []
            for row in results:
                problems.append({
                    "id": row[0],
                    "title": row[1],
                    "difficulty": row[2],
                    "category": row[3],
                    "tags": json.loads(row[4]) if row[4] else [],
                    "acceptance_rate": row[5]
                })
            
            return {"problems": problems}
    except Exception as e:
        logger.error(f"Error fetching problems: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch problems")

@app.get("/api/problems/{problem_id}")
async def get_problem(problem_id: int, user: dict = Depends(require_auth)):
    """Get specific problem details"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT id, title, description, examples, constraints, difficulty, category, tags, test_cases, solution_template
                FROM problems WHERE id = ?
            """, (problem_id,))
            result = await cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Problem not found")
            
            problem = {
                "id": result[0],
                "title": result[1],
                "description": result[2],
                "examples": json.loads(result[3]) if result[3] else [],
                "constraints": json.loads(result[4]) if result[4] else [],
                "difficulty": result[5],
                "category": result[6],
                "tags": json.loads(result[7]) if result[7] else [],
                "test_cases": json.loads(result[8]),
                "solution_template": json.loads(result[9]) if result[9] else {}
            }
            
            return problem
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching problem {problem_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch problem")

@app.get("/api/languages")
async def get_languages():
    """Get supported programming languages"""
    return {"languages": SUPPORTED_LANGUAGES}

@app.post("/api/problems/{problem_id}/chat")
async def chat_with_gpt(
    problem_id: int,
    request: ChatRequest,
    user: dict = Depends(require_auth)
):
    """Chat with GPT about the problem"""
    try:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=503, detail="OpenAI API not configured")
        
        # Get problem details for context
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT title, description, examples, constraints, difficulty, category
                FROM problems WHERE id = ?
            """, (problem_id,))
            problem = await cursor.fetchone()
            
            if not problem:
                raise HTTPException(status_code=404, detail="Problem not found")
        
        # Build context for GPT
        problem_context = f"""
Problem: {problem[0]} (Difficulty: {problem[4]}, Category: {problem[5]})

Description: {problem[1]}

Examples: {problem[2] if problem[2] else 'None provided'}

Constraints: {problem[3] if problem[3] else 'None provided'}
"""
        
        # Build conversation history
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful coding tutor assistant helping students understand programming problems. 
                
Here's the current problem the student is working on:
{problem_context}

Your role is to:
- Help explain the problem statement and requirements
- Guide students through problem-solving approaches
- Explain algorithms and data structures concepts
- Help with debugging and optimization
- Provide hints without giving away the complete solution
- Encourage learning and understanding

Be concise, clear, and educational. Focus on helping the student learn rather than just providing answers."""
            }
        ]
        
        # Add chat history
        for msg in request.chat_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Call OpenAI API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=503, detail=f"OpenAI API error: {response.status_code}")
            
            result = response.json()
            gpt_response = result["choices"][0]["message"]["content"]
            
            return {"response": gpt_response}
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing chat request")

@app.get("/api/judge0/status")
async def check_judge0_status():
    """Check Judge0 API connectivity and configuration"""
    try:
        headers = {}
        if JUDGE0_API_KEY:
            headers.update({
                "X-RapidAPI-Key": JUDGE0_API_KEY,
                "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
            })
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{JUDGE0_API_URL}/languages",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "api_url": JUDGE0_API_URL,
                    "api_key_configured": bool(JUDGE0_API_KEY),
                    "languages_count": len(response.json())
                }
            else:
                return {
                    "status": "error",
                    "api_url": JUDGE0_API_URL,
                    "api_key_configured": bool(JUDGE0_API_KEY),
                    "error": f"HTTP {response.status_code}"
                }
                
    except Exception as e:
        return {
            "status": "disconnected",
            "api_url": JUDGE0_API_URL,
            "api_key_configured": bool(JUDGE0_API_KEY),
            "error": str(e)
        }

@app.post("/api/problems/{problem_id}/run")
async def run_code(
    problem_id: int, 
    request: RunCodeRequest, 
    user: dict = Depends(require_auth)
):
    """Run code against test input"""
    try:
        # Submit to Judge0
        submission = await submit_to_judge0(
            source_code=request.source_code,
            language_id=request.language_id,
            stdin=request.test_input
        )
        
        # Wait for result
        await asyncio.sleep(2)  # Give it a moment to process
        result = await get_submission_result(submission["token"], wait=True)
        
        return {
            "status": result["status"]["description"],
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "time": result.get("time"),
            "memory": result.get("memory"),
            "compile_output": result.get("compile_output", "")
        }
        
    except Exception as e:
        logger.error(f"Error running code: {e}")
        error_detail = "Code execution failed"
        if "judge0" in str(e).lower() or "rapidapi" in str(e).lower():
            error_detail = "Judge0 service unavailable. Please check API configuration."
        elif "timeout" in str(e).lower():
            error_detail = "Code execution timed out. Please optimize your solution."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            error_detail = "Network error connecting to execution service."
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/problems/{problem_id}/submit")
async def submit_solution(
    problem_id: int, 
    request: SubmissionRequest, 
    user: dict = Depends(require_auth)
):
    """Submit solution for judging"""
    try:
        # Get problem test cases
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT test_cases FROM problems WHERE id = ?", (problem_id,))
            result = await cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Problem not found")
            
            test_cases = json.loads(result[0])
        
        # Run against all test cases
        all_passed = True
        total_time = 0
        total_memory = 0
        status = "Accepted"
        
        for i, test_case in enumerate(test_cases):
            submission = await submit_to_judge0(
                source_code=request.source_code,
                language_id=request.language_id,
                stdin=test_case.get("input", ""),
                expected_output=test_case.get("expected_output", "")
            )
            
            await asyncio.sleep(1)
            result = await get_submission_result(submission["token"], wait=True)
            
            if result["status"]["id"] != 3:  # 3 = Accepted in Judge0
                all_passed = False
                status = result["status"]["description"]
                break
            
            total_time += float(result.get("time", 0) or 0)
            total_memory += int(result.get("memory", 0) or 0)
        
        # Calculate averages
        avg_time = total_time / len(test_cases) if test_cases else 0
        avg_memory = total_memory // len(test_cases) if test_cases else 0
        
        # Save submission to database
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO submissions 
                (user_id, problem_id, language_id, source_code, status, runtime, memory_usage, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (user["username"], problem_id, request.language_id, request.source_code, 
                  status, avg_time, avg_memory))
            
            # Update user progress if accepted
            if all_passed:
                # Get problem difficulty
                cursor = await db.execute("SELECT difficulty FROM problems WHERE id = ?", (problem_id,))
                difficulty_result = await cursor.fetchone()
                difficulty = difficulty_result[0] if difficulty_result else "Easy"
                
                # Update progress
                await db.execute("""
                    INSERT OR REPLACE INTO user_progress 
                    (user_id, problems_solved, easy_solved, medium_solved, hard_solved, total_submissions, last_solved_at)
                    VALUES (
                        ?, 
                        COALESCE((SELECT problems_solved FROM user_progress WHERE user_id = ?), 0) + 1,
                        COALESCE((SELECT easy_solved FROM user_progress WHERE user_id = ?), 0) + ?,
                        COALESCE((SELECT medium_solved FROM user_progress WHERE user_id = ?), 0) + ?,
                        COALESCE((SELECT hard_solved FROM user_progress WHERE user_id = ?), 0) + ?,
                        COALESCE((SELECT total_submissions FROM user_progress WHERE user_id = ?), 0) + 1,
                        datetime('now')
                    )
                """, (
                    user["username"], user["username"], user["username"],
                    1 if difficulty == "Easy" else 0,
                    user["username"], 1 if difficulty == "Medium" else 0,
                    user["username"], 1 if difficulty == "Hard" else 0,
                    user["username"]
                ))
            
            await db.commit()
        
        return {
            "status": status,
            "accepted": all_passed,
            "runtime": avg_time,
            "memory": avg_memory,
            "test_cases_passed": len(test_cases) if all_passed else i
        }
        
    except Exception as e:
        logger.error(f"Error submitting solution: {e}")
        error_detail = "Submission failed"
        if "judge0" in str(e).lower() or "rapidapi" in str(e).lower():
            error_detail = "Judge0 service unavailable. Please check API configuration."
        elif "timeout" in str(e).lower():
            error_detail = "Submission timed out. Please optimize your solution."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            error_detail = "Network error connecting to judging service."
        elif "not found" in str(e).lower():
            error_detail = "Problem not found. Please refresh the page."
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/api/user/progress")
async def get_user_progress(user: dict = Depends(require_auth)):
    """Get user's coding progress statistics"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT problems_solved, easy_solved, medium_solved, hard_solved, total_submissions, last_solved_at
                FROM user_progress WHERE user_id = ?
            """, (user["username"],))
            result = await cursor.fetchone()
            
            if result:
                return {
                    "problems_solved": result[0],
                    "easy_solved": result[1],
                    "medium_solved": result[2],
                    "hard_solved": result[3],
                    "total_submissions": result[4],
                    "last_solved_at": result[5]
                }
            else:
                return {
                    "problems_solved": 0,
                    "easy_solved": 0,
                    "medium_solved": 0,
                    "hard_solved": 0,
                    "total_submissions": 0,
                    "last_solved_at": None
                }
    except Exception as e:
        logger.error(f"Error fetching user progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch progress")

@app.post("/api/start-interview")
async def start_interview(request: Request):
    """Start a new interview session with the authenticated user"""
    try:
        user = get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Generate a session ID for the interview
        session_id = str(uuid.uuid4())
        
        # Initialize database and create new interview session
        global current_session_id
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    INSERT INTO interview_sessions (user_email) VALUES (?)
                """, (user.get("email", user.get("username", "")),))
                current_session_id = cursor.lastrowid
                await db.commit()
        except Exception as db_error:
            logger.error(f"Database error in start_interview: {db_error}")
            raise HTTPException(status_code=500, detail="Database error")
        
        return {"session_id": session_id, "user_email": user.get("email", user.get("username", ""))}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in start_interview: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    logger.info(f"WebSocket connection request for session {session_id}")
    try:
        await manager.connect(websocket, session_id)
        logger.info(f"WebSocket connected for session {session_id}")
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "audio":
                # Convert int16 array to bytes
                int16_data = message["data"]
                audio_bytes = struct.pack(f"{len(int16_data)}h", *int16_data)
                await manager.send_audio(session_id, audio_bytes)
            # Note: employee_id handling removed - now using authenticated user email

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        await manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        await manager.disconnect(session_id)

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/database")
async def read_database(request: Request):
    """Database page with authentication check"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return FileResponse("static/database.html")

@app.get("/login")
async def read_login():
    return FileResponse("static/login.html")

@app.get("/problems")
async def read_problems(request: Request):
    """Problems page with authentication check"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return FileResponse("static/problems.html")

@app.get("/problem/{problem_id}")
async def read_problem(problem_id: int, request: Request):
    """Problem solving page with authentication check"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return FileResponse("static/problem.html")

# SQL execution endpoints
@app.post("/api/problems/{problem_id}/run-sql")
async def run_sql_query(
    problem_id: int,
    request: RunCodeRequest,
    http_request: Request
):
    """Execute SQL query for a SQL problem"""
    user = get_current_user(http_request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        async with get_db_connection() as db:
            # Get problem details to verify it's a SQL problem
            cursor = await db.execute("SELECT category FROM problems WHERE id = ?", (problem_id,))
            result = await cursor.fetchone()
            
            if not result or result[0] != 'SQL':
                raise HTTPException(status_code=400, detail="This is not a SQL problem")
            
            # Create a temporary in-memory SQLite database for testing
            test_db_path = f":memory:"
            test_conn = await aiosqlite.connect(test_db_path)
            
            try:
                # For now, we'll provide basic sample tables for testing
                # In production, you'd want to create specific test databases per problem
                await test_conn.execute("""
                    CREATE TABLE sample_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        value INTEGER,
                        created_date DATE
                    )
                """)
                
                await test_conn.execute("""
                    INSERT INTO sample_table (name, value, created_date) VALUES 
                    ('Alice', 100, '2023-01-01'),
                    ('Bob', 200, '2023-01-02'),
                    ('Charlie', 150, '2023-01-03')
                """)
                
                await test_conn.commit()
                
                # Execute the user's SQL query with timeout
                import asyncio
                
                async def execute_query():
                    cursor = await test_conn.execute(request.source_code)
                    return await cursor.fetchall()
                
                # Run with timeout
                try:
                    result = await asyncio.wait_for(execute_query(), timeout=10.0)
                    
                    # Format results for display
                    if result:
                        # Get column names
                        cursor = await test_conn.execute(request.source_code)
                        column_names = [description[0] for description in cursor.description]
                        
                        formatted_result = {
                            "columns": column_names,
                            "rows": result,
                            "row_count": len(result)
                        }
                    else:
                        formatted_result = {
                            "columns": [],
                            "rows": [],
                            "row_count": 0
                        }
                    
                    return {
                        "status": "success",
                        "result": formatted_result,
                        "message": f"Query executed successfully. {len(result) if result else 0} rows returned."
                    }
                    
                except asyncio.TimeoutError:
                    return {
                        "status": "error",
                        "error": "Query timed out after 10 seconds",
                        "message": "Your query took too long to execute. Please optimize it."
                    }
                    
            finally:
                await test_conn.close()
                
    except Exception as e:
        logger.error(f"SQL execution error: {e}")
        return {
            "status": "error", 
            "error": str(e),
            "message": "SQL execution failed. Please check your query syntax."
        }

@app.post("/api/problems/{problem_id}/submit-sql")
async def submit_sql_query(
    problem_id: int,
    request: RunCodeRequest,
    http_request: Request
):
    """Submit SQL query solution for evaluation"""
    user = get_current_user(http_request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        async with get_db_connection() as db:
            # Get problem details
            cursor = await db.execute("SELECT category, solution_template FROM problems WHERE id = ?", (problem_id,))
            result = await cursor.fetchone()
            
            if not result or result[0] != 'SQL':
                raise HTTPException(status_code=400, detail="This is not a SQL problem")
            
            # For SQL problems, we'll do basic syntax validation and execution
            # In a production system, you'd want more sophisticated testing
            test_db_path = f":memory:"
            test_conn = await aiosqlite.connect(test_db_path)
            
            try:
                # Create sample data (same as run endpoint)
                await test_conn.execute("""
                    CREATE TABLE sample_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        value INTEGER,
                        created_date DATE
                    )
                """)
                
                await test_conn.execute("""
                    INSERT INTO sample_table (name, value, created_date) VALUES 
                    ('Alice', 100, '2023-01-01'),
                    ('Bob', 200, '2023-01-02'),
                    ('Charlie', 150, '2023-01-03')
                """)
                
                await test_conn.commit()
                
                # Execute query
                cursor = await test_conn.execute(request.source_code)
                result = await cursor.fetchall()
                
                # For now, just mark as successful if it executes without error
                is_correct = True
                score = 100
                
                # Save submission
                user_id = user["username"]  # Using username as user_id for now
                await db.execute("""
                    INSERT INTO submissions (user_id, problem_id, code, language, status, score, submitted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, problem_id, request.source_code, "sql", "Accepted" if is_correct else "Wrong Answer", score, datetime.now()))
                
                # Update user progress if correct
                if is_correct:
                    cursor = await db.execute("SELECT difficulty FROM problems WHERE id = ?", (problem_id,))
                    difficulty_result = await cursor.fetchone()
                    difficulty = difficulty_result[0] if difficulty_result else "Medium"
                    
                    easy_solved = 1 if difficulty == "Easy" else 0
                    medium_solved = 1 if difficulty == "Medium" else 0
                    hard_solved = 1 if difficulty == "Hard" else 0
                    
                    await db.execute("""
                        INSERT INTO user_progress 
                        (user_id, problems_solved, easy_solved, medium_solved, hard_solved, total_submissions, last_solved_at)
                        VALUES (?, 
                            COALESCE((SELECT problems_solved FROM user_progress WHERE user_id = ?), 0) + 1,
                            COALESCE((SELECT easy_solved FROM user_progress WHERE user_id = ?), 0) + ?,
                            COALESCE((SELECT medium_solved FROM user_progress WHERE user_id = ?), 0) + ?,
                            COALESCE((SELECT hard_solved FROM user_progress WHERE user_id = ?), 0) + ?,
                            COALESCE((SELECT total_submissions FROM user_progress WHERE user_id = ?), 0) + 1,
                            ?
                        )
                        ON CONFLICT(user_id) DO UPDATE SET
                            problems_solved = problems_solved + 1,
                            easy_solved = easy_solved + ?,
                            medium_solved = medium_solved + ?,
                            hard_solved = hard_solved + ?,
                            total_submissions = total_submissions + 1,
                            last_solved_at = ?
                    """, (user_id, user_id, user_id, easy_solved, user_id, medium_solved, user_id, hard_solved, user_id, datetime.now(),
                          easy_solved, medium_solved, hard_solved, datetime.now()))
                
                await db.commit()
                await test_conn.close()
                
                return {
                    "status": "Accepted" if is_correct else "Wrong Answer",
                    "score": score,
                    "message": "Submission successful!" if is_correct else "Query executed but results may not be optimal.",
                    "result": {
                        "columns": [description[0] for description in cursor.description] if result else [],
                        "rows": result,
                        "row_count": len(result) if result else 0
                    }
                }
                
            finally:
                if test_conn:
                    await test_conn.close()
                
    except Exception as e:
        logger.error(f"SQL submission error: {e}")
        return {
            "status": "Runtime Error",
            "score": 0,
            "error": str(e),
            "message": "SQL submission failed. Please check your query."
        }

# Mount static files last to avoid route conflicts
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
