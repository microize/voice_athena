"""Repository for problem data access."""

import json
import logging
from typing import List, Optional, Tuple
import aiosqlite

from ..config.database import get_db
from ..models.schemas import Problem, ProblemListItem, TestCase
from ..core.exceptions import ProblemNotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class ProblemRepository:
    """Repository for problem-related database operations."""
    
    async def get_problems(
        self, 
        difficulty: Optional[str] = None, 
        category: Optional[str] = None
    ) -> List[ProblemListItem]:
        """Get list of problems with optional filtering."""
        try:
            query = "SELECT id, title, difficulty, category, tags, acceptance_rate FROM problems WHERE 1=1"
            params = []
            
            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY id"
            
            async with get_db() as db:
                cursor = await db.execute(query, params)
                results = await cursor.fetchall()
                
                problems = []
                for row in results:
                    problems.append(ProblemListItem(
                        id=row[0],
                        title=row[1],
                        difficulty=row[2],
                        category=row[3],
                        tags=json.loads(row[4]) if row[4] else [],
                        acceptance_rate=row[5]
                    ))
                
                return problems
        except Exception as e:
            logger.error(f"Error fetching problems: {e}")
            raise DatabaseError("Failed to fetch problems")
    
    async def get_problem_by_id(self, problem_id: int) -> Problem:
        """Get specific problem by ID."""
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT id, title, description, examples, constraints, difficulty, 
                           category, tags, test_cases, solution_template, acceptance_rate, created_at
                    FROM problems WHERE id = ?
                """, (problem_id,))
                result = await cursor.fetchone()
                
                if not result:
                    raise ProblemNotFoundError(problem_id)
                
                return Problem(
                    id=result[0],
                    title=result[1],
                    description=result[2],
                    examples=json.loads(result[3]) if result[3] else [],
                    constraints=json.loads(result[4]) if result[4] else [],
                    difficulty=result[5],
                    category=result[6],
                    tags=json.loads(result[7]) if result[7] else [],
                    test_cases=json.loads(result[8]),
                    solution_template=json.loads(result[9]) if result[9] else {},
                    acceptance_rate=result[10],
                    created_at=result[11]
                )
        except ProblemNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching problem {problem_id}: {e}")
            raise DatabaseError(f"Failed to fetch problem {problem_id}")
    
    async def get_test_cases(self, problem_id: int) -> List[TestCase]:
        """Get test cases for a problem."""
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT test_cases FROM problems WHERE id = ?", (problem_id,))
                result = await cursor.fetchone()
                
                if not result:
                    raise ProblemNotFoundError(problem_id)
                
                test_cases_data = json.loads(result[0])
                return [
                    TestCase(
                        input=test_case.get("input", ""),
                        expected_output=test_case.get("expected_output", "")
                    )
                    for test_case in test_cases_data
                ]
        except ProblemNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching test cases for problem {problem_id}: {e}")
            raise DatabaseError(f"Failed to fetch test cases for problem {problem_id}")
    
    async def get_problem_difficulty(self, problem_id: int) -> str:
        """Get difficulty level of a problem."""
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT difficulty FROM problems WHERE id = ?", (problem_id,))
                result = await cursor.fetchone()
                
                if not result:
                    raise ProblemNotFoundError(problem_id)
                
                return result[0]
        except ProblemNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching difficulty for problem {problem_id}: {e}")
            raise DatabaseError(f"Failed to fetch difficulty for problem {problem_id}")
    
    async def create_problem(self, problem: Problem) -> int:
        """Create a new problem and return its ID."""
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    INSERT INTO problems 
                    (title, description, examples, constraints, difficulty, category, tags, test_cases, solution_template, acceptance_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    problem.title,
                    problem.description,
                    json.dumps(problem.examples),
                    json.dumps(problem.constraints),
                    problem.difficulty,
                    problem.category,
                    json.dumps(problem.tags),
                    json.dumps([tc.dict() for tc in problem.test_cases] if hasattr(problem.test_cases[0], 'dict') else problem.test_cases),
                    json.dumps(problem.solution_template),
                    problem.acceptance_rate
                ))
                
                problem_id = cursor.lastrowid
                await db.commit()
                return problem_id
        except Exception as e:
            logger.error(f"Error creating problem: {e}")
            raise DatabaseError("Failed to create problem")
    
    async def update_problem(self, problem_id: int, problem: Problem) -> bool:
        """Update an existing problem."""
        try:
            async with get_db() as db:
                await db.execute("""
                    UPDATE problems SET
                        title = ?, description = ?, examples = ?, constraints = ?,
                        difficulty = ?, category = ?, tags = ?, test_cases = ?,
                        solution_template = ?, acceptance_rate = ?
                    WHERE id = ?
                """, (
                    problem.title,
                    problem.description,
                    json.dumps(problem.examples),
                    json.dumps(problem.constraints),
                    problem.difficulty,
                    problem.category,
                    json.dumps(problem.tags),
                    json.dumps([tc.dict() for tc in problem.test_cases] if hasattr(problem.test_cases[0], 'dict') else problem.test_cases),
                    json.dumps(problem.solution_template),
                    problem.acceptance_rate,
                    problem_id
                ))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating problem {problem_id}: {e}")
            raise DatabaseError(f"Failed to update problem {problem_id}")
    
    async def delete_problem(self, problem_id: int) -> bool:
        """Delete a problem."""
        try:
            async with get_db() as db:
                cursor = await db.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting problem {problem_id}: {e}")
            raise DatabaseError(f"Failed to delete problem {problem_id}")