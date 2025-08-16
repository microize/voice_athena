"""Database query API routes"""
from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
from athena.models.schemas import QueryRequest, ValidatedQueryRequest
from athena.core.security import require_auth
from athena.core.config import settings

router = APIRouter(prefix="/api", tags=["database"])

@router.post("/query")
async def execute_query(request: ValidatedQueryRequest, user: dict = Depends(require_auth)):
    """Execute a SQL query on the interview database"""
    query = request.query.strip()
    
    try:
        async with aiosqlite.connect(settings.DB_PATH) as db:
            cursor = await db.execute(query)
            
            if query.upper().startswith('PRAGMA'):
                # For PRAGMA queries, return all results
                results = await cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                return {
                    "success": True,
                    "columns": columns,
                    "data": results,
                    "row_count": len(results)
                }
            else:
                # For SELECT queries
                results = await cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                return {
                    "success": True,
                    "columns": columns,
                    "data": results,
                    "row_count": len(results)
                }
                
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Query execution failed: {str(e)}"
        )