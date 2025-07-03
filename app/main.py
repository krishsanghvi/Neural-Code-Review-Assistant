import os
from fastapi import FastAPI
from app.api.webhooks import router as webhook_router
from app.api.analytics import router as analytics_router
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Neural Code Review Assistant",
    description="AI-powered code review bot with smart caching and analytics",
    version="2.0.0"
)

# Include routers
app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])


@app.on_event("startup")
async def startup_event():
    print("🚀 Neural Code Review Assistant Starting Up...")
    print(f"📱 GitHub App ID: {settings.github_app_id}")
    print(f"🔑 Private Key Path: {settings.github_private_key_path}")
    print(
        f"🔒 Webhook Secret Set: {'Yes' if settings.github_webhook_secret else 'No'}")
    print(f"🌍 Environment: {settings.environment}")
    print(f"📦 Cache enabled: {os.getenv('ENABLE_CACHE', 'true')}")
    print(f"⚡ Performance monitoring: enabled")
    print("=" * 50)


@app.get("/")
async def root():
    return {
        "message": "Neural Code Review Assistant is running! 🚀",
        "version": "2.0.0",
        "status": "healthy",
        "features": [
            "AI-powered code analysis",
            "Smart caching system",
            "Performance monitoring",
            "Security vulnerability detection",
            "Multi-layer intelligence analysis"
        ]
    }


@app.get("/health")
async def health_check():
    from app.core.cache_manager import cache_manager
    from app.core.performance_monitor import performance_monitor

    cache_stats = cache_manager.get_cache_stats()
    perf_stats = performance_monitor.get_performance_stats()

    return {
        "status": "healthy",
        "environment": settings.environment,
        "cache_enabled": cache_stats["enabled"],
        "cache_hit_rate": f"{cache_stats['hit_rate_percent']:.1f}%",
        "avg_response_time_ms": perf_stats.get("response_times", {}).get("avg_ms", 0),
        "uptime_hours": perf_stats.get("uptime_hours", 0),
        "total_requests": perf_stats.get("total_requests", 0)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
