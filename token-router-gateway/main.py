import time
from fastapi import FastAPI, HTTPException, status
from schemas import RouteRequest, RouteResponse, TokenTelemetry
from cache import check_cache, store_in_cache
from router import dispatch_model

# Initialize the API gateway
app = FastAPI(
    title="Adaptive Token Router & Semantic Gateway",
    description="Cost-aware proxy microservice that routes LLM requests dynamically and caches semantically identical queries.",
    version="1.0.0",
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Uptime monitoring endpoint."""
    return {"status": "healthy", "service": "token-router-gateway"}


@app.post(
    "/api/v1/route",
    response_model=RouteResponse,
    status_code=status.HTTP_200_OK,
)
def route_prompt_endpoint(payload: RouteRequest):
    """
    Main gateway entrypoint:
    1. Evaluates semantic cache (0-token response if hit).
    2. Dynamically routes to Flash or Frontier tier on cache miss.
    3. Stores fresh outputs in cache and returns structured telemetry.
    """
    try:
        start_time = time.time()

        # Step 1: Semantic Cache Check
        cache_hit, cached_text, matched_prompt = check_cache(payload.query)

        if cache_hit and cached_text:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return RouteResponse(
                status="success",
                cached=True,
                routed_tier="cache",
                model_name="chroma-semantic-cache",
                response_text=cached_text,
                telemetry=TokenTelemetry(
                    estimated_prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    latency_ms=elapsed_ms,
                    estimated_cost_usd=0.0,
                    cost_savings_vs_frontier="100.0%",
                ),
            )

        # Step 2: Cache Miss -> Evaluate & Dispatch via Router
        response_text, tier_name, model_name, telemetry = dispatch_model(
            query=payload.query,
            force_tier=payload.force_tier,
        )

        # Step 3: Index new response in semantic cache for future callers
        store_in_cache(
            query=payload.query,
            response_text=response_text,
            model_used=model_name,
        )

        return RouteResponse(
            status="success",
            cached=False,
            routed_tier=tier_name,
            model_name=model_name,
            response_text=response_text,
            telemetry=telemetry,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing execution failure: {str(e)}",
        )