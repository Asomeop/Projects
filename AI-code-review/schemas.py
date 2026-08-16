from typing import List
from pydantic import BaseModel, Field


class CodeIssue(BaseModel):
    line_number: int = Field(
        description="The line number where the issue occurs."
    )
    issue_type: str = Field(
        description="Category of issue: 'Bug', 'Security', or 'Performance'."
    )
    description: str = Field(description="Clear explanation of the problem.")
    suggested_fix: str = Field(
        description="The corrected code snippet or resolution."
    )


class CodeReviewResponse(BaseModel):
    overall_score: int = Field(
        description="Overall code quality score from 1 to 100."
    )
    summary: str = Field(
        description="A concise summary of the overall code quality."
    )
    issues: List[CodeIssue] = Field(
        description="List of detected bugs, security flaws, or inefficiencies."
    )


class ReviewRequest(BaseModel):
    code: str = Field(
        ..., min_length=5, description="The raw source code snippet to analyze."
    )
    language: str = Field(
        default="python",
        description="Programming language of the provided snippet.",
    )


class ReviewApiResponse(BaseModel):
    status: str = Field(default="success")
    execution_time_seconds: float = Field(
        description="Time taken to process and analyze the code snippet."
    )
    data: CodeReviewResponse