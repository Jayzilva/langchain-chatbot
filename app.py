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
    page_title="SDG/ESG/Carbon Consultant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with sustainability theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #2E8B57, #228B22);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2E8B57;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sustainability-card {
        background: linear-gradient(135deg, #f0fff0, #e6ffe6);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #228B22;
        margin: 15px 0px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .chat-message.user {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-left: 4px solid #2196f3;
    }
    .chat-message.bot {
        background: linear-gradient(135deg, #f1f8e9, #dcedc8);
        border-left: 4px solid #4caf50;
    }
    .avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        margin-right: 1rem;
        object-fit: cover;
        border: 2px solid #4caf50;
    }
    .sdg-badge {
        background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 2px;
        display: inline-block;
    }
    .esg-section {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #17a2b8;
    }
    .carbon-metrics {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .consultation-button {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        margin: 5px;
        transition: all 0.3s ease;
    }
    .consultation-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    }
</style>
""", unsafe_allow_html=True)

# SDG and ESG knowledge base
SDG_FRAMEWORK = """
# UN Sustainable Development Goals (SDGs) Framework

## The 17 SDGs:
1. No Poverty
2. Zero Hunger
3. Good Health and Well-Being
4. Quality Education
5. Gender Equality
6. Clean Water and Sanitation
7. Affordable and Clean Energy
8. Decent Work and Economic Growth
9. Industry, Innovation and Infrastructure
10. Reduced Inequalities
11. Sustainable Cities and Communities
12. Responsible Consumption and Production
13. Climate Action
14. Life Below Water
15. Life on Land
16. Peace, Justice and Strong Institutions
17. Partnerships for the Goals

## ESG Framework:
### Environmental (E):
- Climate Change & Carbon Emissions
- Resource Management
- Pollution & Waste
- Biodiversity & Ecosystem Impact

### Social (S):
- Human Rights & Labor Standards
- Community Relations
- Employee Wellbeing
- Supply Chain Ethics

### Governance (G):
- Board Composition & Independence
- Executive Compensation
- Business Ethics & Transparency
- Risk Management

## Carbon Management:
- Scope 1: Direct emissions from owned sources
- Scope 2: Indirect emissions from purchased energy
- Scope 3: All other indirect emissions in value chain
- Carbon Footprint Assessment
- Net Zero Strategies
- Carbon Offset Programs
"""

# Initialize session states
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'business_context' not in st.session_state:
    st.session_state.business_context = ""
if 'consultation_focus' not in st.session_state:
    st.session_state.consultation_focus = "comprehensive"

# Header
st.markdown('<h1 class="main-header">🌱 Sustainability Consultant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">SDG • ESG • Carbon Strategy Advisor</p>', unsafe_allow_html=True)

# Sidebar for sustainability resources and settings
with st.sidebar:

    
    # Model settings
    st.markdown("### ⚙️ Settings")
    model_choice = st.selectbox(
        "AI Model:",
        ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    )
    
    consultation_depth = st.slider(
        "Consultation Depth:",
        min_value=1,
        max_value=5,
        value=4,
        help="1 = Quick insights, 5 = Comprehensive analysis"
    )

# Main consultation interface
st.markdown("### 💬 Sustainability Consultation")

# Business idea input (main area)
if not st.session_state.business_context:
    st.markdown("""
    <div class="sustainability-card">
        <h4>🚀 Get Started</h4>
        <p>Share your business idea or current business operations to receive personalized sustainability consultation covering SDGs, ESG, and carbon management strategies.</p>
    </div>
    """, unsafe_allow_html=True)

# Chat input
user_input = st.text_input(
    "Ask about sustainability strategies, SDG alignment, ESG implementation, or carbon management:",
    placeholder="How can I align my business with SDG goals? What ESG metrics should I track? How do I calculate my carbon footprint?"
)

# Quick consultation buttons
st.markdown("### 🔍 Quick Consultations")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎯 SDG Alignment", key="sdg", help="Analyze SDG alignment opportunities"):
        user_input = "How can my business align with the UN Sustainable Development Goals? Which SDGs are most relevant?"

with col2:
    if st.button("📊 ESG Strategy", key="esg", help="Develop ESG implementation plan"):
        user_input = "What ESG strategies should I implement? How do I measure and report ESG performance?"

with col3:
    if st.button("🌡️ Carbon Plan", key="carbon", help="Create carbon management strategy"):
        user_input = "Help me develop a carbon management plan. How do I measure and reduce my carbon footprint?"

with col4:
    if st.button("📈 Impact Metrics", key="metrics", help="Define sustainability metrics"):
        user_input = "What sustainability metrics should I track? How do I measure my environmental and social impact?"

# Advanced consultation options
with st.expander("🔧 Advanced Consultation Options"):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏭 Industry Analysis", key="industry"):
            user_input = "Provide industry-specific sustainability recommendations and benchmarks for my business sector."
        if st.button("💰 Green Finance", key="finance"):
            user_input = "What green financing options are available? How do I access sustainable investment opportunities?"
    with col2:
        if st.button("📋 Compliance Check", key="compliance"):
            user_input = "What sustainability regulations and standards apply to my business? How do I ensure compliance?"
        if st.button("🤝 Stakeholder Engagement", key="stakeholder"):
            user_input = "How do I engage stakeholders in sustainability initiatives? What communication strategies work best?"

# Consultation depth instructions
depth_instructions = {
    1: "Provide concise, actionable insights focusing on immediate priorities.",
    2: "Give clear recommendations with basic implementation steps.",
    3: "Offer balanced analysis with practical examples and next steps.",
    4: "Provide comprehensive consultation with detailed strategies and metrics.",
    5: "Deliver in-depth analysis with extensive recommendations, case studies, and implementation roadmaps."
}

# Enhanced system prompt for sustainability consultation
system_prompt = f"""
You are an expert Sustainability Consultant specializing in SDG (Sustainable Development Goals), ESG (Environmental, Social, Governance), and Carbon Management strategies.

CONSULTATION CONTEXT:
Business/Idea: {st.session_state.business_context if st.session_state.business_context else "General business consultation"}
Focus Area: Comprehensive Analysis

FRAMEWORKS TO REFERENCE:
{SDG_FRAMEWORK}

CONSULTATION APPROACH:
{depth_instructions[consultation_depth]}

RESPONSE STRUCTURE:
1. **Immediate Opportunities**: Quick wins and low-hanging fruit
2. **Strategic Recommendations**: Medium to long-term strategies
3. **Implementation Roadmap**: Step-by-step guidance
4. **Metrics & KPIs**: How to measure success
5. **Risk Mitigation**: Potential challenges and solutions

TONE: Professional, practical, and encouraging. Focus on actionable insights that can drive real sustainability impact.

Always consider:
- Industry-specific sustainability challenges
- Regulatory requirements and standards
- Stakeholder expectations
- Financial implications and ROI
- Implementation feasibility
- Measurement and reporting requirements
"""

# Process user input and generate consultation
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Set up the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Consultation Request: {question}")
    ])
    
    # OpenAI LLM
    llm = ChatOpenAI(model=model_choice, temperature=0.7)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    
    # Display consultation in progress
    with st.spinner("🌱 Analyzing sustainability opportunities..."):
        try:
            response = chain.invoke({'question': user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"⚠️ Consultation error: {str(e)}")

# Display chat history with enhanced styling
if st.session_state.chat_history:
    st.markdown("### 📋 Consultation History")
    
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <img src="https://img.icons8.com/color/48/000000/businessman.png" class="avatar">
                <div>
                    <b>👤 You</b>
                    <br>{message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot">
                <img src="https://img.icons8.com/color/48/000000/leaf.png" class="avatar">
                <div>
                    <b>🌱 Sustainability Consultant</b>
                    <br>{message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Action buttons
if st.session_state.chat_history:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 New Consultation", key="new_consultation"):
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        if st.button("📥 Export Consultation", key="export"):
            # Create consultation report
            consultation_text = "\n\n".join([
                f"{'USER' if msg['role'] == 'user' else 'CONSULTANT'}: {msg['content']}"
                for msg in st.session_state.chat_history
            ])
            st.download_button(
                label="📄 Download Report",
                data=consultation_text,
                file_name=f"sustainability_consultation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    with col3:
        if st.button("📊 Generate Action Plan", key="action_plan"):
            action_plan_prompt = "Based on our consultation, create a prioritized action plan with timelines and resources needed for implementing the sustainability recommendations."
            st.session_state.chat_history.append({"role": "user", "content": action_plan_prompt})
            
            with st.spinner("🎯 Creating your action plan..."):
                try:
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        ("user", "Create Action Plan: {question}")
                    ])
                    llm = ChatOpenAI(model=model_choice, temperature=0.3)
                    chain = prompt | llm | StrOutputParser()
                    response = chain.invoke({'question': action_plan_prompt})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Error generating action plan: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    🌍 <strong>Sustainability Consultant</strong> • Powered by AI • Making business more sustainable, one consultation at a time
</div>
""", unsafe_allow_html=True)