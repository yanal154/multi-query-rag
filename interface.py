import streamlit as st
from chatbot import generate_response

st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f4;
        font-family: 'Arial', sans-serif;
    }
    .main {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Intelligent Document Retrieval")
st.write("Enter your question below to generate an answer based on document .")

with st.container():
    user_question = st.text_area("Your Question:", height=100, placeholder="Type your question here...")

answer_placeholder = st.empty()

if st.button("Submit"):
    if user_question.strip():
        with st.spinner("Processing your question..."):
            answer = generate_response(user_question)
        answer_placeholder.markdown("**Answer:**\n\n" + answer)
    else:
        st.warning("Please enter a question before submitting.")
        
with st.sidebar:
    st.header("About the Application")
    st.write("This application uses artificial intelligence for document retrieval and question answering.")
    st.write("It is powered by LangChain, ChromaDB, and OpenAI for precise answers.")


st.markdown("<br><br>", unsafe_allow_html=True)
