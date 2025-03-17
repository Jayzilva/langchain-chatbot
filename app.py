from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import streamlit as st
import os
from dotenv import load_dotenv
import time
import random
import pandas as pd
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Langchain tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Learning Mentor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4f8bf9;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .answer-container {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4f8bf9;
        margin: 10px 0px;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #e6f3ff;
    }
    .chat-message.bot {
        background-color: #f8f9fa;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

# Load the curriculum file
try:
    with open("curriculum.md", "r") as file:
        curriculum_content = file.read()
except FileNotFoundError:
    # Sample curriculum content if file doesn't exist
    curriculum_content = """
    # Sample Curriculum

    ## Module 1: Introduction
    - Overview of the subject
    - Key terminology
    - Historical context
    
    ## Module 2: Core Concepts
    - Fundamental principles
    - Theoretical frameworks
    - Practical applications
    
    ## Module 3: Advanced Topics
    - Specialized techniques
    - Current research
    - Future directions
    """

# Initialize session states
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'question' not in st.session_state:
    st.session_state.question = ""

# Sidebar for curriculum overview and settings
with st.sidebar:
    # Using a real image for the sidebar logo
   #st.image("https://img.freepik.com/free-photo/graduation-cap-diploma-with-red-ribbon_23-2148076043.jpg", width=100)
    st.markdown("## Learning Resources")
    
    # Display curriculum sections
    with st.expander("View Curriculum Outline", expanded=False):
        st.markdown(curriculum_content)
    
    # Topic suggestions based on curriculum
    st.markdown("### Suggested Topics")
    topics = ["Introduction to the Course", "Key Concepts", "Practice Exercises", "Quiz Preparation", "Project Ideas"]
    selected_topic = st.selectbox("Quick Access:", topics)
    
    if st.button("Explore Topic"):
        st.session_state.question = f"Tell me about {selected_topic}"
    
    # Model settings
    st.markdown("### Settings")
    model_choice = st.selectbox(
        "Select Model:",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    )
    
    response_length = st.slider(
        "Response Detail Level:",
        min_value=1,
        max_value=5,
        value=3,
        help="1 = Brief, 5 = Comprehensive"
    )



# Chat input
user_input = st.text_input("What would you like to learn today?", key="user_input", value=st.session_state.question)

# Clear st.session_state.question after using it
st.session_state.question = ""

# Custom buttons for common queries
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Explain a concept"):
        user_input = "Can you explain the most important concept in this curriculum?"
with col2:
    if st.button("Practice exercises"):
        user_input = "Can you give me some practice exercises related to the curriculum?"
with col3:
    if st.button("Learning path"):
        user_input = "What's the recommended learning path for this curriculum?"
with col4:
    if st.button("Study tips"):
        user_input = "What are some effective study strategies for this material?"

# Prepare the system prompt with curriculum content and response detail
detail_level_instructions = {
    1: "Provide very brief, concise responses focusing only on key points.",
    2: "Keep explanations short but include essential details.",
    3: "Balance detail with clarity in your explanations.",
    4: "Provide comprehensive explanations with examples where helpful.",
    5: "Give detailed, in-depth explanations with multiple examples and elaborations."
}

system_prompt = f"""
You are a helpful assistant and a personal mentor. You are familiar with the following curriculum:
{curriculum_content}

{detail_level_instructions[response_length]}

Please respond to the user queries based on the curriculum, helping them navigate through the learning material and providing guidance as a mentor.
Use friendly, encouraging language and occasionally ask follow-up questions to check understanding.
"""

# Chat interface
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Set up the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "Question: {question}")
        ]
    )
    
    # OpenAI LLM
    llm = ChatOpenAI(model=model_choice)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    
    # Display a spinner while processing
    with st.spinner("Thinking..."):
        try:
            response = chain.invoke({'question': user_input})
            # Add response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user">
            <img src="https://img.freepik.com/free-photo/portrait-white-man-isolated_53876-40306.jpg" class="avatar">
            <div>
                <b>You</b>
                <br>{message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot">
            <img src="https://img.freepik.com/free-photo/3d-render-teacher-character-design_23-2150898834.jpg" class="avatar">
            <div>
                <b>Learning Mentor</b>
                <br>{message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Clear chat option
if st.session_state.chat_history and st.button("Clear Conversation"):
    st.session_state.chat_history = []
    st.rerun()