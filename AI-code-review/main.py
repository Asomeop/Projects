import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

class CodeIssue(BaseModel):
    line_number: int = Field(
        description="The line number where the issue occurs."
    )
    issue_type: str = Field(
        description="Category of issue: 'Bug', 'Security', or 'Performance'."
    )
    description: str = Field(
        description="Clear explanation of the problem."
    )
    suggested_fix: str = Field(
        description="The corrected code snippet or detailed resolution."
    )

class CodeReviewResponse(BaseModel):
    overall_score: int = Field(
        description="Overall code quality score from 1 (terrible) to 100 (perfect)."
    )
    summary: str = Field(
        description="A concise summary of the overall code quality."
    )
    issues: List[CodeIssue] = Field(
        description="List of detected bugs, security flaws, or inefficiencies."
    )

# Initialize LLM and attach schema enforcement
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
structured_llm = llm.with_structured_output(CodeReviewResponse)

def review_code(code_snippet: str, language: str = "python") -> CodeReviewResponse:
    prompt = f"""
    You are a Senior Security Analyst and Lead Software Engineer.
    Analyze the following {language} code snippet for bugs, security vulnerabilities, and bad practices.

    Code Snippet:
    ```{language}
    {code_snippet}
    ```
    """

    # Invoke the model; it returns a CodeReviewResponse instance directly
    return structured_llm.invoke(prompt)

if __name__ == "__main__":
    # Test script locally on a flawed code snippet
    test_code = """
    def get_user_data(user_id):
        query = "SELECT * FROM users WHERE id = " + user_id
        cursor.execute(query)
        return cursor.fetchall()
    """

    print("Analyzing code snippet...")
    review = review_code(test_code, "python")

    print("\n[REVIEW OVERVIEW]")
    print(f"Score: {review.overall_score}/100")
    print(f"Summary: {review.summary}\n")

    print("[ISSUES FOUND]")
    for issue in review.issues:
        print(f"- [{issue.issue_type}] Line {issue.line_number}: {issue.description}")
        print(f"  Fix: {issue.suggested_fix}\n")