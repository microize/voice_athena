# Athena Coding Platform Setup Guide

## 🎯 Overview
Your coding platform is now fully implemented and ready for use! This guide covers setup, configuration, and usage.

## ✅ Implemented Features

### Core Functionality
- **Problem Database**: 4 LeetCode-style problems with multiple difficulty levels
- **Multi-language Support**: Python, JavaScript, Java, C++, C#
- **Monaco Editor**: Full-featured code editor with syntax highlighting
- **Code Execution**: Judge0 API integration for running and testing code
- **Submission System**: Complete solution testing against all test cases
- **User Progress Tracking**: Track problems solved by difficulty level
- **Authentication**: Secure login system with session management

### User Interface
- **Problems List Page** (`/problems`): Browse and filter problems
- **Problem Solver Page** (`/problem/{id}`): Code editor with problem details
- **Navigation Component**: Consistent navigation across all pages
- **Responsive Design**: Works on desktop and mobile devices

### Technical Features
- **Database Schema**: SQLite with proper relationships and indexes
- **API Endpoints**: RESTful API for all operations
- **Error Handling**: Comprehensive error handling and user feedback
- **Performance Metrics**: Runtime and memory usage tracking
- **Security**: Input validation and secure authentication

## 🚀 Quick Start

### 1. Start the Server
```bash
cd /mnt/c/0.sripathi/project/ocean/athena/voice_athena/voice_athena/app
uv run python server.py
```

### 2. Access the Application
- Main page: http://localhost:8002/
- Login page: http://localhost:8002/login
- Problems list: http://localhost:8002/problems
- Database interface: http://localhost:8002/database

### 3. Login Credentials
Use these test accounts:
- Username: `admin`, Password: `admin`
- Username: `test`, Password: `test123`
- Username: `user`, Password: `password`

## 📁 File Structure

```
app/
├── server.py                 # Main FastAPI server
├── interview_sessions.db     # SQLite database
├── .env                      # Environment variables
├── static/
│   ├── index.html           # Main page
│   ├── login.html           # Login page
│   ├── problems.html        # Problems list
│   ├── problem.html         # Problem solver
│   ├── database.html        # Database interface
│   └── components/
│       ├── nav-component.js # Navigation component
│       ├── nav-component.html
│       └── nav-component.css
```

## ⚙️ Configuration

### Judge0 API (Optional)
For code execution, you can use:

1. **Free Judge0 Instance** (Recommended for testing):
   - Set `JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com`
   - Get free API key from RapidAPI
   - Add to `.env`: `JUDGE0_API_KEY=your-rapidapi-key`

2. **Self-hosted Judge0** (Production):
   - Follow Judge0 installation guide
   - Set `JUDGE0_API_URL=http://your-judge0-instance:2358`
   - Leave `JUDGE0_API_KEY` empty

### Environment Variables
Edit `.env` file:
```env
JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=your-rapidapi-key-here
```

## 🧪 Testing

### 1. Database Test
```bash
uv run python -c "
import asyncio, aiosqlite
async def test():
    async with aiosqlite.connect('interview_sessions.db') as db:
        cursor = await db.execute('SELECT COUNT(*) FROM problems')
        print(f'Problems in database: {(await cursor.fetchone())[0]}')
asyncio.run(test())
"
```

### 2. API Test
```bash
curl http://localhost:8002/api/problems
```

### 3. Full System Test
The comprehensive test has already been run and passed ✅

## 📊 Database Schema

### Problems Table
- `id`: Problem ID
- `title`: Problem title
- `description`: Problem description with examples
- `difficulty`: Easy/Medium/Hard
- `category`: Problem category
- `test_cases`: JSON array of test cases
- `solution_template`: JSON object with code templates

### User Progress Table
- `user_id`: User identifier
- `problems_solved`: Total problems solved
- `easy_solved`: Easy problems solved
- `medium_solved`: Medium problems solved
- `hard_solved`: Hard problems solved
- `total_submissions`: Total submissions count

### Submissions Table
- `user_id`: User who submitted
- `problem_id`: Problem attempted
- `language_id`: Programming language used
- `source_code`: Submitted code
- `status`: Accepted/Wrong Answer/etc.
- `runtime`: Execution time
- `memory_usage`: Memory consumed

## 🎮 Usage Guide

### For Students/Users:

1. **Login**: Use provided credentials
2. **Browse Problems**: Go to `/problems` to see available challenges
3. **Solve Problems**: Click on any problem to open the code editor
4. **Test Code**: Use "Run" button to test with sample input
5. **Submit Solution**: Use "Submit" button to test against all cases
6. **Track Progress**: View your statistics on the problems page

### For Administrators:

1. **Add Problems**: Use the database interface or add directly to SQL
2. **Monitor Usage**: Check submissions and user progress tables
3. **Manage Users**: Add/remove users in the authentication system
4. **View Reports**: Access interview session data for analysis

## 🔧 Customization

### Adding New Problems:
```sql
INSERT INTO problems (title, description, difficulty, category, test_cases, solution_template)
VALUES (
    'Problem Title',
    'Problem description...',
    'Easy',
    'Array',
    '[{"input": "test", "expected_output": "result"}]',
    '{"python": "def solution():\n    pass"}'
);
```

### Adding New Languages:
1. Add language ID to `SUPPORTED_LANGUAGES` in `server.py`
2. Update language selector in `problem.html`
3. Add templates to problem solution_template JSON

## 🚨 Troubleshooting

### Common Issues:

1. **Port Already in Use**: Change port in `server.py` or kill existing process
2. **Database Locked**: Close any open database connections
3. **Judge0 Timeout**: Check API key and network connectivity
4. **Monaco Editor Not Loading**: Check CDN availability

### Logs and Debugging:
- Server logs: Check console output
- Client logs: Open browser developer tools
- Database: Use SQLite browser for direct access

## 🎉 Success!

Your coding platform is now fully operational with:
- ✅ 4 sample problems ready to solve
- ✅ Multi-language code execution
- ✅ User authentication and progress tracking
- ✅ Professional UI with Monaco editor
- ✅ Complete submission and testing system

The platform is ready for educational use, coding interviews, or algorithm practice!