
import os
import csv
import logging
from dotenv import load_dotenv
import pandas as pd
from langchain_groq.chat_models import ChatGroq
from langchain.chains import  RetrievalQA
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
load_dotenv()

path = "app/api/data/cleaned_merged_data.csv"
data = pd.read_csv(path)


"""# Converting dataFrame into Document (Data-To-Text)"""

def get_test_type(row):
    test_types = []
    cols = ['Ability&Aptitude', 'Biodata&SituationalJudgement', 'Competencies', 'Development&360',
            'AssessmentExercies', 'Knowledge&Skills', 'Personality&Behavior', 'Simulation']
    for col in cols:
        if row[col] == 1:
            test_types.append(col)
    return ",".join(test_types)

def create_document_content(row):
    test_types = get_test_type(row)
    page_content = f"""
    Assessment name: {row['Assessment Name']}
    Remote Testing Support: {row['Remote Testing Support']}
    Adaptive/IRT Support: {row['Adaptive/IRT Support']}
    Description: {row['Description']}
    Duration: {row['Duration']}
    Test Type(s): {test_types}
    """
    metadata = {
        "name": row["Assessment Name"],
        "url": row["Assessment URL"],
        "remote_support": row["Remote Testing Support"],
        "adaptive_support": row["Adaptive/IRT Support"],
        "duration": row["Duration"],
        "test_type": test_types
    }
    return Document(page_content = page_content.strip(), metadata=metadata)

document_data = [create_document_content(row) for _, row in data.iterrows()]

document_data[0]

model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embedding_model = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2",
                                        model_kwargs = model_kwargs,
                                        encode_kwargs = encode_kwargs)

vectorstore = FAISS.from_documents(document_data, embedding_model)

vectorstore.save_local("app/api/data/FAISSVectorStore")

"""# LLama Model"""

llm = ChatGroq(model = "llama3-8b-8192", api_key = GROQ_API_KEY, temperature = 0.6)
llm

retriever = vectorstore.as_retriever(search_kwargs={"k": 10},score_threshold = 0.6,search_type ="similarity" )
retriever

QA_chain = RetrievalQA.from_chain_type(
    llm = llm,
    retriever=retriever,
    return_source_documents=True,
    verbose = True
)

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

def display_results(results):
    if not results:
        return "No matching tests found."
    df = pd.DataFrame(results)
    print(df.to_markdown(index=False))
    return df

def ask_question(query: str):
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
        response = QA_chain.invoke({
            "query": system_prompt + "\n" + query  })

        docs = response.get("source_documents", [])
        formatted_results = format_response(docs)
        formatted_results = formatted_results[:10]

        return {
            "answer": response["result"],
            "recommendations": formatted_results
        }
    except Exception as e:
        logging.error(f"Error in ask_question: {str(e)}", exc_info=True)
        return {"recommendations": []}

def get_recommendations(query):
    """Main entry function to get structured recommendations."""
    try:
        response = ask_question(query)
        print("\nAnswer from LLM:")
        return display_results(response["recommendations"])
    except Exception as e:
        logging.error(f"Error in get_recommendations: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


QUERY = """I am hiring for an analyst and wants applications to screen using Cognitive and personality tests, what options are available within 45 mins."""


if __name__ == "__main__":
    query = QUERY
    recommendations = get_recommendations(query)


