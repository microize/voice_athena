"""Problems API routes"""
import logging
import httpx
import json
import asyncio
import aiosqlite
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from athena.core.config import settings
from athena.models.schemas import ChatRequest, RunCodeRequest, SubmissionRequest
from athena.core.security import require_auth
from athena.services.problem_service import ProblemService
from athena.services.judge0_service import Judge0Service
from athena.core.dependencies import get_problem_service

router = APIRouter(prefix="/api", tags=["problems"])
logger = logging.getLogger(__name__)

@router.get("/problems")
async def get_problems(
    difficulty: Optional[str] = None, 
    category: Optional[str] = None, 
    user: dict = Depends(require_auth),
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Get list of problems with optional filtering"""
    try:
        user_id = user.get("username")  # Using username as user_id
        problems = await problem_service.get_problems(difficulty, category, user_id)
        return {"problems": [problem.model_dump() for problem in problems]}
    except Exception as e:
        logger.error(f"Error fetching problems: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch problems")

@router.get("/problems/{problem_id}")
async def get_problem(
    problem_id: int, 
    user: dict = Depends(require_auth),
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Get specific problem details"""
    try:
        problem = await problem_service.get_problem_by_id(problem_id)
        
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        return problem.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching problem {problem_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch problem")

@router.get("/languages")
async def get_languages():
    """Get supported programming languages"""
    return {"languages": settings.SUPPORTED_LANGUAGES}

@router.post("/problems/{problem_id}/chat")
async def chat_with_gpt(
    problem_id: int,
    request: ChatRequest,
    user: dict = Depends(require_auth)
):
    """Chat with GPT about the problem"""
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=503, detail="OpenAI API not configured")
        
        # Get problem details for context using service
        problem_service = get_problem_service()
        problem_context_data = await problem_service.get_problem_context(problem_id)
        
        if not problem_context_data:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Build context for GPT
        problem_context = f"""
Problem: {problem_context_data['title']} (Difficulty: {problem_context_data['difficulty']}, Category: {problem_context_data['category']})

Description: {problem_context_data['description']}

Examples: {problem_context_data['examples'] if problem_context_data['examples'] else 'None provided'}

Constraints: {problem_context_data['constraints'] if problem_context_data['constraints'] else 'None provided'}
"""
        
        # Build conversation messages
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
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
        
        # Call OpenAI API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
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
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing chat request")

@router.get("/judge0/status")
async def check_judge0_status():
    """Check Judge0 API connectivity and configuration"""
    try:
        headers = {}
        if settings.JUDGE0_API_KEY:
            headers.update({
                "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
                "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
            })
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.JUDGE0_API_URL}/languages",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "api_url": settings.JUDGE0_API_URL,
                    "api_key_configured": bool(settings.JUDGE0_API_KEY),
                    "languages_count": len(response.json())
                }
            else:
                return {
                    "status": "error",
                    "api_url": settings.JUDGE0_API_URL,
                    "api_key_configured": bool(settings.JUDGE0_API_KEY),
                    "error": f"HTTP {response.status_code}"
                }
                
    except Exception as e:
        return {
            "status": "disconnected",
            "api_url": settings.JUDGE0_API_URL,
            "api_key_configured": bool(settings.JUDGE0_API_KEY),
            "error": str(e)
        }

@router.post("/problems/{problem_id}/run")
async def run_code(
    problem_id: int, 
    request: RunCodeRequest, 
    user: dict = Depends(require_auth)
):
    """Run code against test input"""
    try:
        result = await Judge0Service.execute_code(
            source_code=request.source_code,
            language_id=request.language_id,
            test_input=request.test_input
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error running code: {e}")
        if "judge0" in str(e).lower() or "rapidapi" in str(e).lower():
            error_detail = "Judge0 service unavailable. Please check API configuration."
        elif "timeout" in str(e).lower():
            error_detail = "Code execution timed out. Please optimize your solution."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            error_detail = "Network error connecting to execution service."
        else:
            error_detail = "Code execution failed"
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/problems/{problem_id}/submit")
async def submit_solution(
    problem_id: int, 
    request: SubmissionRequest, 
    user: dict = Depends(require_auth)
):
    """Submit solution for judging"""
    try:
        # Get problem test cases
        async with aiosqlite.connect(settings.DB_PATH) as db:
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
            submission = await Judge0Service.submit_to_judge0(
                source_code=request.source_code,
                language_id=request.language_id,
                stdin=test_case.get("input", ""),
                expected_output=test_case.get("expected_output", "")
            )
            
            await asyncio.sleep(1)
            result = await Judge0Service.get_submission_result(submission["token"], wait=True)
            
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
        async with aiosqlite.connect(settings.DB_PATH) as db:
            await db.execute("""
                INSERT INTO submissions 
                (user_id, problem_id, language_id, source_code, status, runtime, memory_usage, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user["username"], problem_id, request.language_id, request.source_code,
                  status, avg_time, avg_memory, datetime.now()))
            
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
                        ?
                    )
                """, (
                    user["username"], user["username"], user["username"],
                    1 if difficulty == "Easy" else 0,
                    user["username"], 1 if difficulty == "Medium" else 0,
                    user["username"], 1 if difficulty == "Hard" else 0,
                    user["username"],
                    datetime.now()
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
        if "judge0" in str(e).lower() or "rapidapi" in str(e).lower():
            error_detail = "Judge0 service unavailable. Please check API configuration."
        elif "timeout" in str(e).lower():
            error_detail = "Submission timed out. Please optimize your solution."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            error_detail = "Network error connecting to judging service."
        elif "not found" in str(e).lower():
            error_detail = "Problem not found. Please refresh the page."
        else:
            error_detail = "Submission failed"
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/problems/{problem_id}/run-sql")
async def run_sql_query(
    problem_id: int,
    request: RunCodeRequest,
    user: dict = Depends(require_auth)
):
    """Execute SQL query for a SQL problem"""
    try:
        async with aiosqlite.connect(settings.DB_PATH) as db:
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

@router.post("/problems/{problem_id}/submit-sql")
async def submit_sql_query(
    problem_id: int,
    request: RunCodeRequest,
    user: dict = Depends(require_auth)
):
    """Submit SQL query solution for evaluation"""
    try:
        async with aiosqlite.connect(settings.DB_PATH) as db:
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
                    INSERT INTO submissions (user_id, problem_id, language_id, source_code, status, runtime, memory_usage, submitted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, problem_id, 0, request.source_code, "Accepted" if is_correct else "Wrong Answer", 
                      0, 0, datetime.now()))
                
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