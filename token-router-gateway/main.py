import os
import time
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from schemas import RouteRequest, RouteResponse, TokenTelemetry
from cache import check_cache, store_in_cache
from router import dispatch_model

app = FastAPI(
    title="Adaptive Token Router & Semantic Gateway",
    description="Cost-aware proxy microservice that routes LLM requests dynamically and caches semantically identical queries.",
    version="1.0.0",
)

# Allowed origins: local dev environments and optional custom environment URL
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

env_frontend_url = os.getenv("FRONTEND_URL")
if env_frontend_url:
    allowed_origins.append(env_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if env_frontend_url else ["*"],  # Fallback to wildcard until production domain is finalized
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "service": "token-router-gateway"}

@app.post("/api/v1/route", response_model=RouteResponse, status_code=status.HTTP_200_OK)
def route_prompt_endpoint(payload: RouteRequest):
    try:
        start_time = time.time()
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

        response_text, tier_name, model_name, telemetry = dispatch_model(
            query=payload.query,
            force_tier=payload.force_tier,
        )

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