"""
FastAPI application for LLM Analysis Quiz Solver
"""
import logging
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json

from config import Config
from quiz_solver import QuizSolver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
is_valid, error_msg = Config.validate()
if not is_valid:
    logger.error(f"Configuration error: {error_msg}")
    raise ValueError(f"Invalid configuration: {error_msg}")

# Create FastAPI app
app = FastAPI(
    title="LLM Analysis Quiz Solver",
    description="An intelligent quiz-solving application using LLMs",
    version="1.0.0"
)


class QuizRequest(BaseModel):
    """Request model for quiz solving"""
    email: str = Field(..., description="Student email address")
    secret: str = Field(..., description="Secret string for verification")
    url: str = Field(..., description="Quiz URL to solve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "secret": "my-secret-string",
                "url": "https://example.com/quiz-834"
            }
        }


class QuizResponse(BaseModel):
    """Response model for quiz solving"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


@app.post("/solve", response_model=QuizResponse)
async def solve_quiz(request: QuizRequest):
    """
    Main endpoint for solving quizzes
    
    Validates the secret and starts the quiz-solving process.
    The actual solving happens asynchronously.
    """
    try:
        # Verify secret
        if request.secret != Config.SECRET:
            logger.warning(f"Invalid secret provided for email: {request.email}")
            raise HTTPException(
                status_code=403,
                detail="Invalid secret"
            )
        
        # Verify email matches (optional additional check)
        if request.email != Config.EMAIL:
            logger.warning(f"Email mismatch: {request.email} vs {Config.EMAIL}")
            # Still allow, but log it
        
        logger.info(f"Received quiz request for URL: {request.url}")
        
        # Create quiz solver
        solver = QuizSolver(email=request.email, secret=request.secret)
        
        # Start solving asynchronously (don't block the response)
        # Run in background task
        asyncio.create_task(solver.solve_quiz(request.url))
        
        # Return immediate response
        return QuizResponse(
            success=True,
            message="Quiz solving started",
            details={
                "url": request.url,
                "email": request.email
            }
        )
    
    except HTTPException:
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request")
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        logger.error(f"Error processing quiz request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/solve-sync", response_model=QuizResponse)
async def solve_quiz_sync(request: QuizRequest):
    """
    Synchronous endpoint for solving quizzes (waits for completion)
    
    Use this for testing, but be aware it may take up to 3 minutes.
    """
    try:
        # Verify secret
        if request.secret != Config.SECRET:
            logger.warning(f"Invalid secret provided for email: {request.email}")
            raise HTTPException(
                status_code=403,
                detail="Invalid secret"
            )
        
        logger.info(f"Received synchronous quiz request for URL: {request.url}")
        
        # Create quiz solver
        solver = QuizSolver(email=request.email, secret=request.secret)
        
        # Solve quiz and wait for result
        result = await solver.solve_quiz(request.url)
        
        return QuizResponse(
            success=result.get('success', False),
            message="Quiz solving completed" if result.get('success') else "Quiz solving failed",
            details=result
        )
    
    except HTTPException:
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request")
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        logger.error(f"Error processing quiz request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LLM Analysis Quiz Solver"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LLM Analysis Quiz Solver",
        "version": "1.0.0",
        "endpoints": {
            "/solve": "POST - Start solving a quiz (async)",
            "/solve-sync": "POST - Solve a quiz and wait for result",
            "/health": "GET - Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )

