"""Judge0 API service for code execution"""
import asyncio
import httpx
import logging
from typing import Dict, Any, Optional

from athena.core.config import settings
from athena.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class Judge0Service:
    """Service for interacting with Judge0 code execution API"""
    
    @staticmethod
    async def submit_to_judge0(
        source_code: str, 
        language_id: int, 
        stdin: str = "", 
        expected_output: str = ""
    ) -> Dict[str, Any]:
        """Submit code to Judge0 for execution"""
        headers = {
            "Content-Type": "application/json",
        }
        
        # Add RapidAPI headers if using hosted version
        if settings.JUDGE0_API_KEY:
            headers.update({
                "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
                "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
            })
        
        submission_data = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin or "",
            "expected_output": expected_output or ""
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.JUDGE0_API_URL}/submissions",
                    json=submission_data,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error submitting to Judge0: {e}")
                raise ExternalServiceError("Code execution service unavailable")

    @staticmethod
    async def get_submission_result(token: str, wait: bool = False) -> Dict[str, Any]:
        """Get submission result from Judge0"""
        headers = {}
        if settings.JUDGE0_API_KEY:
            headers.update({
                "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
                "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
            })
        
        params = {}
        if wait:
            params["wait"] = "true"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.JUDGE0_API_URL}/submissions/{token}",
                    headers=headers,
                    params=params,
                    timeout=60.0 if wait else 10.0
                )
                response.raise_for_status()
                result = response.json()
                
                return result
            except Exception as e:
                logger.error(f"Error getting submission result: {e}")
                raise ExternalServiceError("Failed to get execution results")

    @staticmethod
    async def execute_code(
        source_code: str,
        language_id: int,
        test_input: str = "",
        expected_output: str = ""
    ) -> Dict[str, Any]:
        """Execute code and return results (submit + wait for result)"""
        try:
            # Submit to Judge0
            submission = await Judge0Service.submit_to_judge0(
                source_code=source_code,
                language_id=language_id,
                stdin=test_input,
                expected_output=expected_output
            )
            
            # Wait for result
            await asyncio.sleep(2)  # Give it a moment to process
            result = await Judge0Service.get_submission_result(submission["token"], wait=True)
            
            return {
                "status": result["status"]["description"],
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "time": result.get("time"),
                "memory": result.get("memory"),
                "compile_output": result.get("compile_output", ""),
                "token": submission["token"]
            }
            
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            error_detail = "Code execution failed"
            if "judge0" in str(e).lower() or "rapidapi" in str(e).lower():
                error_detail = "Judge0 service unavailable. Please check API configuration."
            elif "timeout" in str(e).lower():
                error_detail = "Code execution timed out. Please optimize your solution."
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                error_detail = "Network error connecting to execution service."
            raise ExternalServiceError(error_detail)

    @staticmethod
    async def test_connectivity() -> Dict[str, Any]:
        """Test Judge0 API connectivity and configuration"""
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