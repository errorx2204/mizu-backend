from fastapi import FastAPI

app = FastAPI(title="MIZU API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "MIZU API is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}