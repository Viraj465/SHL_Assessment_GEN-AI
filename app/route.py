from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
# from app.api.services.llmService import get_recommendations

router = APIRouter()

class Query(BaseModel):
    question: str
    history: list = []

class RecommendationResponse(BaseModel):
    answer: str
    recommendations: list

@router.post("/Hello")
async def hello_world():
    return {"message": "Hello, World!"}
# @router.post("/recommendations/", response_model=RecommendationResponse)
# async def get_recommendations(query: Query):
#     try:
#         response = get_recommendations(query.question, query.history)
#         return {"answer":response['answer'],
#                 "recommendations":response['recommendations']}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    