import os
import json
import csv
import pandas as pd
from typing import Dict, List, Optional
from langchain_groq.chat_models import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from sentence_transformers import SentenceTransformer
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.output_parsers import PydanticOutputParser
from langchain_community.document_loaders import csv_loader
import logging
from dotenv import load_dotenv
load_dotenv()

# Groq API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# path to the CSV file
path = os.getenv('PATH')
data = pd.read_csv(path)
data=data.drop("Unnamed: 0",axis = 1)

# LangChain Model with Message History
def get_test_type(row):
    test_types = []
    cols = ['Ability&Aptitude',
        'Biodata&SituationalJudgement', 'Competencies', 'Developemnt&360',
        'AssessmentExercies', 'Knowledge&Skills', 'Personality&Behavior',
        'Simulation']
    for col in cols:
        if row[col ] == 1:
            test_types.append(col)
    return ",".join(test_types)

def create_document(row):
    metadata = {
            "name": row["Assessment Name"],
            "url": row["Assessment URL"],
            "remote_support": row["Remote Testing Support"],
            "adaptive_support": row["Adaptive/IRT Support"],
            "duration": row["Duration"],
            "test_type": get_test_type(row)
        }

    return Document(page_content = row['Description'], metadata=metadata)

docs = [create_document(row) for _, row in data.iterrows()]

# Embedding model and vectorstore
embedding_model = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embedding_model)

# Memory and LLM
memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
llm = ChatGroq(model="llama-3.3-70b-versatile",
               api_key = GROQ_API_KEY)

# QA_Chain
QA_chain = ConversationalRetrievalChain.from_llm(
    llm = llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
    memory=memory,
    return_source_documents=True,
    verbose = True
)

# Define the Pydantic model for structured output
def format_response(response_docs):
    results = []
    for doc in response_docs:
        meta = doc.metadata
        results.append({
            "Assessment Name": meta.get("name"),
            "URL": meta.get("url"),
            "Remote Support": meta.get("remote_support"),
            "Adaptive Support": meta.get("adaptive_support"),
            "Duration": meta.get("duration"),
            "Test Type": meta.get("test_type")
        })
    return results

def ask_question(query: str, history=[]):
    response = QA_chain.invoke({"question": query})
    docs = response.get("source_documents", [])
    formatted_results = format_response(docs)
    formatted_results = formatted_results[:10]

    return {
        "answer": response["answer"],
        "recommendations": formatted_results
    }

def display_results(results):
    if not results:
        return "No matching tests found."
    df = pd.DataFrame(results)
    return df

def get_recommendations(query):
    try:
        response = ask_question(query)
        print(f"Answer: {response['answer']}\n")
        print("Recommended Tests:")
        return display_results(response["recommendations"])
    except Exception as e:
        logging.error(f"Error getting recommendations: {str(e)}")
        return f"Error: {str(e)}"
    


if __name__ == "__main__":
    query = input("Enter your job description or requirements: ")
    recommendations = get_recommendations(query)
    print(recommendations)
    # Save the recommendations to a CSV file
    recommendations.to_csv("recommendations.csv", index=False)
    print("Recommendations saved to recommendations.csv")