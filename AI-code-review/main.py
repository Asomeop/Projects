import time
from fastapi import FastAPI, HTTPException, status
from schemas import ReviewRequest, ReviewApiResponse
from reviewer import analyze_code

# Initialize FastAPI application with clear metadata
app = FastAPI(
    title="AI Code Reviewer & Security Analysis API",
    description="Microservice providing automated code quality and security reviews via LLMs.",
    version="1.0.0",
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Simple health check endpoint for monitoring uptime."""
    return {"status": "healthy"}


@app.post(
    "/api/v1/review",
    response_model=ReviewApiResponse,
    status_code=status.HTTP_200_OK,
)
def review_code_endpoint(payload: ReviewRequest):
    """
    Analyzes submitted code snippet for bugs, security vulnerabilities,
    and performance issues, measuring total execution latency.
    """
    try:
        # 1. Start timer to track model latency
        start_time = time.time()

        # 2. Invoke Gemini analysis engine from reviewer.py
        review_result = analyze_code(
            code_snippet=payload.code,
            language=payload.language,
        )

        # 3. Calculate total elapsed time
        elapsed_time = round(time.time() - start_time, 3)

        # 4. Return structured envelope matching ReviewApiResponse schema
        return ReviewApiResponse(
            status="success",
            execution_time_seconds=elapsed_time,
            data=review_result,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing code review: {str(e)}",
        )