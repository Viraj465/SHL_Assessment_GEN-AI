from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.route import router

app = FastAPI(
    title="SHL Assessment Recommendation System API",
    description="API for recommending SHL assessments",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello, Welcome to SHL Assessment Recommender API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)