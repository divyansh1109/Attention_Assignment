from fastapi import FastAPI
from pydantic import BaseModel
import requests
from database import ResearchDatabase
from agents import FutureWorksAgent, QnAAgent

app = FastAPI()
db = ResearchDatabase()

# Define request models
class PaperSearchRequest(BaseModel):
    topic: str
    limit: int = 5

# Initialize the agents
future_agent = FutureWorksAgent()
qna_agent = QnAAgent()

@app.on_event("shutdown")
async def shutdown():
    pass

@app.get("/search_papers/{topic}")
async def search_papers(topic: str, limit: int = 5):
    papers = db.get_papers_by_topic(topic, limit)
    if not papers:
        papers = db.fetch_papers_from_arxiv(topic, limit)
    return {"papers": papers}

# @app.post("/suggest_future_works/")
# async def suggest_future_works(context: str):
#     future_work_suggestions = future_agent.suggest_future_works(context)
#     return {"future_work_suggestions": future_work_suggestions}

# @app.post("/answer_question/")
# async def answer_question(question: str, context: str):
#     answer = qna_agent.answer_question(question, context)
#     return {"answer": answer}

# Streamlit frontend
import streamlit as st

def streamlit_app():
    st.title('Research Paper Search and Future Works')
    st.write("Enter a topic to fetch the latest research papers")
    
    topic = st.text_input("Enter topic:", "")
    if topic:
        response = requests.get(f"http://127.0.0.1:8000/search_papers/{topic}")
        if response.status_code == 200:
            papers = response.json().get("papers", [])
            if papers:
                for i, paper in enumerate(papers):
                    st.write(f"### {i+1}. {paper['title']}")
                    st.write(f"**Authors**: {', '.join(paper['authors'])}")
                    st.write(f"**Published Date**: {paper['published_date']}")
                    st.write(f"**Summary**: {paper['summary']}")
            else:
                st.write("No papers found.")
        else:
            st.write("Error fetching papers.")

if __name__ == "__main__":
    streamlit_app()