from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from route import router
import os

os.system("apt-get update && apt-get install git-lfs -y")
os.system("git lfs install")
os.system("git lfs pull")

app = FastAPI(
    title="SHL Assessment Recommendation System API",
    description="API for recommending SHL assessments",
    version="1.0.0"
)

# origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

app.mount("/",StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return {"message": "Hello, Welcome to SHL Assessment Recommender API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=True)