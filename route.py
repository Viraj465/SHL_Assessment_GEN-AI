from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq.chat_models import ChatGroq
from langchain.chains import  RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import pandas as pd
from dotenv import load_dotenv
import os
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")
router = APIRouter()

class Query(BaseModel):
    query: str
    history: list = []

class Recommendation(BaseModel):
    assessment_name: str
    url: str
    remote_support: str
    adaptive_support: str
    duration: str
    test_type: str

class RecommendationResponse(BaseModel):
    answer: str
    recommendations: List[Recommendation]

    @classmethod
    def from_dataframe(cls, answer: str, df: pd.DataFrame):
        """Helper method to create response from DataFrame"""
        return cls(
            answer=answer,
            recommendations=df.to_csv(index=False)
        )

try:
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'} 
    )
    vectorstore = FAISS.load_local(
        "app/api/data/vectorstore/shl_faiss", 
        embeddings,
        allow_dangerous_deserialization=True
    )
    logger.info("Successfully loaded embeddings and vector store")
except Exception as e:
    logger.error(f"Error initializing embeddings or vector store: {str(e)}")
    raise

memory = ConversationBufferMemory(
    memory_key="chat_history",
    output_key="answer",
    return_messages=True,
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
    memory=memory,
    return_source_documents=True,
    verbose=True
)

@router.post("/Hello")
async def hello_world():
    return {"message": "Hello, World vite + react!"}


def format_response(response_docs):
    results = []
    for doc in response_docs:
        meta = doc.metadata
        results.append({
            "Assessment Name": meta.get("name",""),
            "URL": meta.get("url",""),
            "Remote Support": meta.get("remote_support",""),
            "Adaptive Support": meta.get("adaptive_support",""),
            "Duration": meta.get("duration",""),
            "Test Type": meta.get("test_type","")
        })
    return results[:10]


@router.post("/recommendations/", response_model=RecommendationResponse)
async def get_recommendations(query: Query):
    try:
        logger.debug(f"Received query: {query.query} with history: {query.history}")
        response = qa.invoke({
            "question":query.query,
            "chat_history": query.history
        })
        logger.debug(f"Respaonse from QA: {response}")

        recommendations = [
            Recommendation(
                assessment_name=str(meta.get("name", "")),
                url=str(meta.get("url", "")),
                remote_support=str(meta.get("remote_support", "")),
                adaptive_support=str(meta.get("adaptive_support", "")),
                duration=str(meta.get("duration", "")),
                test_type=str(meta.get("test_type", ""))
            )
            for doc in response.get("source_documents", [])
            for meta in [doc.metadata]
        ][:10]

        return RecommendationResponse(
            answer = response.get("answer", ""),
            recommendations = recommendations
        )
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    