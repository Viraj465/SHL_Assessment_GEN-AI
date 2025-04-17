from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from typing import List,Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from huggingface_hub import hf_hub_download
from langchain_groq.chat_models import ChatGroq
from langchain.chains import  RetrievalQA
import pandas as pd
from dotenv import load_dotenv
import os
import logging
import tempfile
import shutil


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

router = APIRouter()


CACHE_DIR = tempfile.mkdtemp()
os.environ['TRANSFORMERS_CACHE'] = CACHE_DIR
os.environ['HF_HOME'] = CACHE_DIR

FAISS_INDEX_PATH = hf_hub_download(
    repo_id="Viraj0112/SHL_Assessment",
    filename="app/api/data/FAISSvectorstore/index.faiss",
    repo_type="space"
)
FAISS_STORE_FOLDER = os.path.dirname(FAISS_INDEX_PATH)

def initialize_models():
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False},
        )
        vectorstore = FAISS.load_local(
            FAISS_STORE_FOLDER,
            embedding_model,
            allow_dangerous_deserialization=True
        )
        llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY, temperature=0.6)
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 10},
            score_threshold=0.6,
            search_type="similarity"
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            verbose=True
        )
        logger.info("Successfully initialized all models and chains")
        return qa_chain
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        raise
    
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

# QA_CHAIN = initialize_models()

@router.post("/Hello")
async def hello_world():
    return {"message": "Hello, World vite + react!"}


def format_response(response_docs):
    """Format the documents into a structured output."""
    results = []
    for doc in response_docs:
        meta = doc.metadata
        results.append({
            "Assessment Name": meta.get("name", "N/A"),
            "URL": meta.get("url", "N/A"),
            "Remote Support": meta.get("remote_support", "N/A"),
            "Adaptive Support": meta.get("adaptive_support", "N/A"),
            "Duration": meta.get("duration", "N/A"),
            "Test Type": meta.get("test_type", "N/A")
        })
    return results


MAX_RETRIES = 3
QA_CHAIN = None

for attempt in range(MAX_RETRIES):
    try:
        QA_CHAIN = initialize_models()
        break
    except Exception as e:
        logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
        if attempt == MAX_RETRIES - 1:
            logger.error("All initialization attempts failed")
            raise

@router.post("/recommendations/", response_model=RecommendationResponse)
async def get_recommendations(query: Query):
    system_prompt = (
    "Based on the following requirements, analyze the retrieved assessment documents and recommend "
    "the most suitable tests that match ALL of these criteria:\n"
    "1. Tests that cover the specific skills mentioned\n"
    "2. Tests within the requested time constraints\n"
    "3. Tests with appropriate remote/adaptive features if specified\n"
    "4. Tests that matches the required job designation mentioned properly\n"
    "Explain why each recommendation is suitable for the requirements."
    )
    try:
        logger.debug(f"Received query: {query.query} with history: {query.history}")
        if QA_CHAIN is None:
            raise HTTPException(
            status_code=503,
            detail="Service unavailable - Model initialization failed"
            )
        response = QA_CHAIN.invoke({
        "query": system_prompt + "\n" + query.query,
    })
        logger.debug(f"Response from QA: {response}")
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
            answer=response["result"],
            recommendations=recommendations )
    
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    