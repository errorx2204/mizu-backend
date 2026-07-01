from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, transaction, budget, insights

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
