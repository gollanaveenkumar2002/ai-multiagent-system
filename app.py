import os
import sys
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix UnicodeEncodeError on Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import streamlit as st
from autogen import ConversableAgent

# Set page configuration
st.set_page_config(page_title="EdTech Marketing Agents", layout="wide")

st.title("🤖 EdTech Marketing AI Agents")
st.markdown("Explore AI-driven marketing strategies and internal debates between C-suite AI agents.")

# Sidebar for API Configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Use environment variable as backup if no input provided
if not api_key:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.sidebar.success("API Key loaded from .env file ✅")

if not api_key:
    st.sidebar.warning("Please enter an API Key to proceed.")
    st.stop()

llm_config = {
    "model": "gpt-4o-mini",
    "api_key": api_key,
}

# Tabs for different functionalities
tab1, tab2 = st.tabs(["📢 Marketing Strategist", "👔 C-Suite Debate"])

# --- Tab 1: Marketing Strategist ---
with tab1:
    st.header("Marketing Strategist Agent")
    st.write("Ask the strategist for B2B/B2C growth strategies.")

    # User input
    default_prompt = "I want some solid marketing strategies for B2B promotions for my project management courses."
    user_input = st.text_area("Your Request", value=default_prompt, height=100)

    if st.button("Generate Strategy"):
        with st.spinner("Consulting the Strategist..."):
            try:
                agent_mkt_str = ConversableAgent(
                    name="marketing_strategist",
                    system_message=(
                        "You are an expert marketing strategist for both B2B and B2C businesses. "
                        "Your expertise lies in creating growth and go-to-market strategies "
                        "for companies and products in the EdTech industry."
                    ),
                    llm_config=llm_config,
                    human_input_mode="NEVER",
                    code_execution_config=False,
                )

                reply = agent_mkt_str.generate_reply(
                    messages=[{"role": "user", "content": user_input}]
                )
                
                st.subheader("Strategy Response")
                
                # generate_reply can return a string or a dict depending on config
                if isinstance(reply, dict):
                    st.markdown(reply.get("content", ""))
                else:
                    st.markdown(str(reply))
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- Tab 2: CMO vs CEO Debate ---
with tab2:
    st.header("CMO vs CEO Discussion")
    st.write("Simulate a debate between the CMO (B2B focus) and CEO (B2C focus).")

    initial_msg = st.text_input("CMO's Opening Argument", "I think we should focus more on B2B business for our project management courses")

    if st.button("Start Debate"):
        with st.spinner("Agents are debating..."):
            try:
                # Agent Definitions
                CMO_Agent = ConversableAgent(
                    name="CMO",
                    system_message=(
                        "You are a Chief Marketing Officer in an EdTech company. "
                        "You are discussing with the CEO whether you should focus more on B2B or B2C for project management courses. "
                        "As the CMO, you want to focus on B2B."
                    ),
                    llm_config=llm_config,
                    code_execution_config=False,
                    human_input_mode="NEVER",
                )

                CEO_Agent = ConversableAgent(
                    name="CEO",
                    system_message=(
                        "You are the CEO of an EdTech company. "
                        "You are discussing with the CMO whether you should focus more on B2B or B2C for project management courses. "
                        "As the CEO, you want to focus on B2C."
                    ),
                    llm_config=llm_config,
                    code_execution_config=False,
                    human_input_mode="NEVER",
                )

                # Initiate Chat
                result = CMO_Agent.initiate_chat(
                    CEO_Agent,
                    message=initial_msg,
                    max_turns=3,
                    silent=True, # Suppress stdout to keep console clean
                    summary_method="reflection_with_llm"
                )

                # Display Chat History
                st.subheader("Discussion History")
                
                # The chat history is stored in result.chat_history
                # Structure: List of dictionaries with 'content', 'role' (but role is relative to the agent holding the history)
                # It's often easier to iterate through the history object
                
                for message in result.chat_history:
                    # Message structure: {'content': '...', 'role': 'assistant'/'user', 'name': '...'}
                    # In autogen, the 'name' field usually tells us who spoke.
                    
                    sender_name = message.get('name', 'Unknown')
                    content = message.get('content', '')
                    
                    # Choose a defined avatar or style
                    if sender_name == "CMO":
                        avatar = "👔"
                    elif sender_name == "CEO":
                        avatar = "🕴️"
                    else:
                        avatar = "🤖"

                    with st.chat_message(sender_name, avatar=avatar):
                        st.markdown(f"**{sender_name}:** {content}")

                st.divider()
                st.subheader("Debate Summary")
                st.info(result.summary)
                st.write(f"**Cost usage:** {result.cost}")

            except Exception as e:
                st.error(f"An error occurred during the debate: {e}")
