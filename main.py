from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ultra-lightweight health check - responds instantly without loading anything
async def health_startup(scope, receive, send):
    """ASGI app that responds instantly to /health without loading FastAPI"""
    if scope["type"] == "http" and scope.get("path") == "/health":
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"status":"healthy","source":"startup"}',
        })
    else:
        # Pass through to main app
        await app(scope, receive, send)

# Main FastAPI app
app = FastAPI(
    title="MIZU API",
    description="Backend API for MIZU Finance App",
    version="1.0.0"
)

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api import auth, transaction, budget, insights
app.include_router(auth.router)
app.include_router(transaction.router)
app.include_router(budget.router)
app.include_router(insights.router)

@app.get("/")
def root():
    return {
        "message": "MIZU API is running",
        "status": "healthy",
        "version": "1.0.0",
        "database": "Supabase PostgreSQL"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
