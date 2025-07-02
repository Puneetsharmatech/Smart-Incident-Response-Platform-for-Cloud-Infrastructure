# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="SIRP Backend API",
    description="Smart Incident Response Platform Backend API for Cloud Infrastructure",
    version="0.1.0",
)

@app.get("/")
async def read_root():
    return {"message": "Hello from SIRP Backend!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)