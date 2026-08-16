import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from schemas import CodeReviewResponse

# Load environment variables (GOOGLE_API_KEY)
load_dotenv()

# Initialize Gemini with deterministic settings (temperature=0)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)

# Enforce structured output matching our Pydantic schema
structured_llm = llm.with_structured_output(CodeReviewResponse)


def analyze_code(code_snippet: str, language: str = "python") -> CodeReviewResponse:
    """
    Invokes Gemini to analyze a code snippet for bugs, security vulnerabilities,
    and performance issues, returning structured output.
    """
    prompt = f"""
    You are a Senior Security Analyst and Principal Backend Engineer.
    Conduct a rigorous static code review on the following {language} snippet.
    Identify bugs, security vulnerabilities, and bad practices.

    Code Snippet:
    ```{language}
    {code_snippet}
    ```
    """
    return structured_llm.invoke(prompt)