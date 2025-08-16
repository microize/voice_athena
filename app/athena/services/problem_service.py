"""Problem-related database operations"""
import json
from typing import List, Optional, Dict, Any
import aiosqlite

from athena.core.config import settings
from athena.core.logging_config import get_logger
from athena.core.exceptions import DatabaseError, ProblemNotFoundError
from athena.models.schemas import Problem, ProblemListItem, ProblemDetail

logger = get_logger("services.problem")

class ProblemService:
    """Service class for problem-related database operations"""
    
    @staticmethod
    async def get_problems(
        difficulty: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ProblemListItem]:
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
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute(query, params)
                results = await cursor.fetchall()
                
                problems = []
                for row in results:
                    problem = ProblemListItem(
                        id=row[0],
                        title=row[1],
                        difficulty=row[2],
                        category=row[3],
                        tags=json.loads(row[4]) if row[4] else [],
                        acceptance_rate=row[5]
                    )
                    problems.append(problem)
                
                return problems
                
        except Exception as e:
            logger.error(f"Error fetching problems: {e}")
            raise DatabaseError(f"Failed to fetch problems: {str(e)}")
    
    @staticmethod
    async def get_problem_by_id(problem_id: int) -> Optional[ProblemDetail]:
        """Get specific problem details by ID"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT id, title, description, examples, constraints, difficulty, 
                           category, tags, test_cases, solution_template
                    FROM problems WHERE id = ?
                """, (problem_id,))
                result = await cursor.fetchone()
                
                if not result:
                    raise ProblemNotFoundError(problem_id)
                
                problem = ProblemDetail(
                    id=result[0],
                    title=result[1],
                    description=result[2],
                    examples=json.loads(result[3]) if result[3] else [],
                    constraints=json.loads(result[4]) if result[4] else [],
                    difficulty=result[5],
                    category=result[6],
                    tags=json.loads(result[7]) if result[7] else [],
                    test_cases=json.loads(result[8]) if result[8] else {},
                    solution_template=json.loads(result[9]) if result[9] else {}
                )
                
                return problem
                
        except Exception as e:
            logger.error(f"Error fetching problem {problem_id}: {e}")
            raise
    
    @staticmethod
    async def get_problem_context(problem_id: int) -> Optional[Dict[str, Any]]:
        """Get problem context for chat/AI assistance"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT title, description, examples, constraints, difficulty, category
                    FROM problems WHERE id = ?
                """, (problem_id,))
                result = await cursor.fetchone()
                
                if not result:
                    return None
                
                return {
                    "title": result[0],
                    "description": result[1],
                    "examples": result[2],
                    "constraints": result[3],
                    "difficulty": result[4],
                    "category": result[5]
                }
                
        except Exception as e:
            logger.error(f"Error fetching problem context {problem_id}: {e}")
            raise
    
    @staticmethod
    async def create_problem(problem_data: Problem) -> int:
        """Create a new problem"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute("""
                    INSERT INTO problems (
                        title, description, examples, constraints, difficulty,
                        category, tags, test_cases, solution_template, acceptance_rate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    problem_data.title,
                    problem_data.description,
                    problem_data.examples,
                    problem_data.constraints,
                    problem_data.difficulty,
                    problem_data.category,
                    problem_data.tags,
                    problem_data.test_cases,
                    problem_data.solution_template,
                    problem_data.acceptance_rate
                ))
                problem_id = cursor.lastrowid
                await db.commit()
                
                logger.info(f"Created problem {problem_id}: {problem_data.title}")
                return problem_id
                
        except Exception as e:
            logger.error(f"Error creating problem: {e}")
            raise
    
    @staticmethod
    async def update_problem(problem_id: int, problem_data: Problem) -> bool:
        """Update an existing problem"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                await db.execute("""
                    UPDATE problems SET
                        title = ?, description = ?, examples = ?, constraints = ?,
                        difficulty = ?, category = ?, tags = ?, test_cases = ?,
                        solution_template = ?, acceptance_rate = ?
                    WHERE id = ?
                """, (
                    problem_data.title,
                    problem_data.description,
                    problem_data.examples,
                    problem_data.constraints,
                    problem_data.difficulty,
                    problem_data.category,
                    problem_data.tags,
                    problem_data.test_cases,
                    problem_data.solution_template,
                    problem_data.acceptance_rate,
                    problem_id
                ))
                await db.commit()
                
                logger.info(f"Updated problem {problem_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating problem {problem_id}: {e}")
            raise
    
    @staticmethod
    async def delete_problem(problem_id: int) -> bool:
        """Delete a problem"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                await db.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
                await db.commit()
                
                logger.info(f"Deleted problem {problem_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting problem {problem_id}: {e}")
            raise