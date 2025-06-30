from fastapi import FastAPI
from app.api.webhooks import router as webhook_router
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Neural Code Review Assistant",
    description="AI-powered code review bot for GitHub",
    version="1.0.0"
)

# Include routers
app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])


@app.on_event("startup")
async def startup_event():
    print("🚀 Neural Code Review Assistant Starting Up...")
    print(f"📱 GitHub App ID: {settings.github_app_id}")
    print(f"🔑 Private Key Path: {settings.github_private_key_path}")
    print(
        f"🔒 Webhook Secret Set: {'Yes' if settings.github_webhook_secret else 'No'}")
    print(f"🌍 Environment: {settings.environment}")
    print("=" * 50)


@app.get("/")
async def root():
    return {
        "message": "Neural Code Review Assistant is running! 🚀",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True if settings.environment == "development" else False
    )
