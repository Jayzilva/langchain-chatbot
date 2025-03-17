from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Langchain tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# Load the curriculum file
with open("curriculum.md", "r") as file:
    curriculum_content = file.read()

# Prepare the system prompt with curriculum content
system_prompt = f"""
You are a helpful assistant and a personal mentor. You are familiar with the following curriculum:
{curriculum_content}

Please respond to the user queries based on the curriculum, helping them navigate through the learning material and providing guidance as a mentor.
"""

# Set up the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", "Question: {question}")
    ]
)

# Streamlit interface
st.title('Langchain Demo With OPENAI API')
input_text = st.text_input("Search the topic you want")

# OpenAI LLM
llm = ChatOpenAI(model="gpt-4o-mini")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Display the output based on user input
if input_text:
    st.write(chain.invoke({'question': input_text}))
