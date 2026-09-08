import os
import time
from typing import Tuple
from dotenv import load_dotenv
import tiktoken
from google import genai
from schemas import TokenTelemetry

load_dotenv()

# Official Google GenAI client (picks up GEMINI_API_KEY from environment)
client = genai.Client()

# Fast BPE tokenizer encoding
tokenizer = tiktoken.get_encoding("cl100k_base")

# Pricing per million tokens (Tier 1: Flash vs. Tier 2: Frontier benchmark)
PRICING = {
    "gemini-2.5-flash": {
        "input_per_m": 0.15,
        "output_per_m": 0.60
    },
    "frontier-reasoning": {
        "input_per_m": 3.00,
        "output_per_m": 15.00
    }
}


def count_tokens(text: str) -> int:
    """Calculates exact token count locally in microseconds."""
    return len(tokenizer.encode(text))

def classify_complexity(prompt: str, token_count: int) -> Tuple[str, str]:
    """
    Evaluates query complexity to select optimal model tier.
    Returns (tier_name, model_name).
    """
    # High token volume or explicit reasoning indicators trigger Tier 2
    complex_keywords = [
        "derive", "mathematical proof", "architect", "refactor system",
        "vulnerability analysis", "concurrency", "optimize algorithm"
    ]

    is_complex = token_count > 600 or any(kw in prompt.lower() for kw in complex_keywords)

    if is_complex:
        # Tier 2: Frontier reasoning model (or heavy thinking mode)
        return "tier-2-frontier", "gemini-3.1-pro-preview"
    
    # Tier 1: Fast, highly cost-effective workhorse
    return "tier-1-flash", "gemini-2.5-flash"


def dispatch_model(query: str, force_tier: str = None) -> Tuple[str, str, str, TokenTelemetry]:
    """
    Routes query to appropriate model tier, executes call, and computes telemetry.
    Returns (response_text, tier_name, model_name, telemetry).
    """
    prompt_tokens = count_tokens(query)

    # 1. Determine tier (allow manual override if supplied)
    if force_tier == "tier-2-frontier":
        tier_name, model_name = "tier-2-frontier", "gemini-3.1-pro-preview"
    elif force_tier == "tier-1-flash":
        tier_name, model_name = "tier-1-flash", "gemini-2.5-flash"
    else:
        tier_name, model_name = classify_complexity(query, prompt_tokens)

    # 2. Execute LLM call and measure roundtrip latency
    start_time = time.time()
    response = client.models.generate_content(
        model=model_name,
        contents=query
    )
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    response_text = response.text or ""
    completion_tokens = count_tokens(response_text)
    total_tokens = prompt_tokens + completion_tokens

    # 3. Calculate financial cost
    pricing_tier = PRICING["gemini-2.5-flash"] if "flash" in model_name else PRICING["frontier-reasoning"]
    actual_cost = (
        (prompt_tokens / 1_000_000) * pricing_tier["input_per_m"]
        + (completion_tokens / 1_000_000) * pricing_tier["output_per_m"]
    )

    # Cost if this had run on a frontier model
    frontier_cost = (
        (prompt_tokens / 1_000_000) * PRICING["frontier-reasoning"]["input_per_m"]
        + (completion_tokens / 1_000_000) * PRICING["frontier-reasoning"]["output_per_m"]
    )

    savings_pct = (
        round(((frontier_cost - actual_cost) / frontier_cost) * 100, 1)
        if frontier_cost > 0 else 0.0
    )

    telemetry = TokenTelemetry(
        estimated_prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=elapsed_ms,
        estimated_cost_usd=round(actual_cost, 6),
        cost_savings_vs_frontier=f"{savings_pct}%"
    )

    return response_text, tier_name, model_name, telemetry