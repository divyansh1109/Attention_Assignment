import streamlit as st
import requests
from agents import QnAAgent, FutureWorksAgent  

st.title("Academic Research Paper Assistant")

API_BASE_URL = "http://localhost:8000"  # URL for FastAPI server

topic = st.text_input("Enter a research topic:")

# Initialize papers if not already present in session state
if "papers" not in st.session_state:
    st.session_state.papers = []

future_work = FutureWorksAgent()

# Search papers on button click
if st.button("Search Papers"):
    response = requests.get(f"http://127.0.0.1:8000/search_papers/{topic}")
    if response.status_code == 200:
        st.session_state.papers = response.json().get("papers", [])
        if st.session_state.papers:
            for paper in st.session_state.papers:
                
                st.write(f"**Title:** {paper['title']}")
                st.write(f"**Year:** {paper['year']}")
                st.write(f"**Abstract:** {paper['abstract']}")
                try:
                    f_work = future_work.suggest_future_works(paper['abstract'])
                    st.write(f_work)
                except Exception as e:
                    st.write(f"Error generating Future Work: {str(e)}")
                    
        else:
            st.write("No papers found for the given topic.")
    else:
        st.write(f"Error fetching papers: {response.status_code}")

# Q&A Section
st.subheader("Ask Questions About the Papers")
question = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if st.session_state.papers:
        context = " ".join([paper['abstract'] for paper in st.session_state.papers])
        qna_agent = QnAAgent()
        
        try:
            answer = qna_agent.answer_question(question, context)
            st.write(answer)
        except Exception as e:
            st.write(f"Error generating answer: {str(e)}")
    else:
        st.write("Please search for papers first.")
