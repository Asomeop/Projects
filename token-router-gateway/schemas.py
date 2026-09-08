from typing import Optional
from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        description="The prompt or sub-agent task to be routed."
    )
    force_tier: Optional[str] = Field(
        default=None,
        description="Optional manual override: 'tier-1-flash' or 'tier-2-frontier'."
    )

class TokenTelemetry(BaseModel):
    estimated_prompt_tokens: int = Field(
        description="Raw prompt token count calculated locally before model call."
    )
    completion_tokens: int = Field(
        description="Tokens generated in the model output."
    )
    total_tokens: int = Field(
        description="Sum of prompt and completion tokens."
    )
    latency_ms: float = Field(
        description="Total roundtrip execution time in milliseconds."
    )
    estimated_cost_usd: float = Field(
        description="Inference cost calculated from model pricing tiers."
    )
    cost_savings_vs_frontier: str = Field(
        description="Estimated percentage saved compared to running on a frontier model."
    )


class RouteResponse(BaseModel):
    status: str = Field(default="success")
    cached: bool = Field(
        description="True if the query was resolved via semantic cache at 0 token cost."
    )
    routed_tier: str = Field(
        description="The model tier selected: 'cache', 'tier-1-flash', or 'tier-2-frontier'."
    )
    model_name: str = Field(
        description="Exact model identifier that processed the request."
    )
    response_text: str = Field(
        description="The generated output text from the model or cache."
    )
    telemetry: TokenTelemetry