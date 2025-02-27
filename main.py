import os
import time
import streamlit as st
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
BASE_URL = f"{os.environ.get('API_ENDPOINT')}/api/v1"

def navigate_to(module_name):
    st.session_state["selected_module"] = module_name
    st.rerun()

def generate_token():
    st.title("Vantage Financial Agile UI - Prototype (Subatomic)")
    st.header("Authentication & Token Generation")
    
    st.markdown("""
    Please enter your secret security key to authenticate and retrieve an access token.
    """)
    
    secret_code = st.text_input("Security Key:", type="password")
    if st.button("Generate Access Token"):
        response = requests.post(f"{BASE_URL}/auth/token", json={"security_key": secret_code})
        if response.status_code == 200:
            token = response.json().get("access_token", "")
            st.session_state["token"] = token
            st.session_state["authenticated"] = True
            navigate_to("Dashboard")
        else:
            st.error("Authentication failed. Please check your security key and try again.")

def main_menu():
    st.title("Vantage Financial Agile UI - Prototype (Subatomic)")
    st.header("Dashboard")
    
    st.markdown("""
    Welcome to the main dashboard. Select a module to proceed.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    if col1.button("💬 Intelligent Assistant", use_container_width=True):
        navigate_to("Intelligent Assistant")
    if col2.button("🧠 Advanced Reasoning", use_container_width=True):
        navigate_to("Advanced Reasoning")
    if col3.button("🤖 AI-Powered Agent", use_container_width=True):
        navigate_to("AI-Powered Agent")


def chat_ui():
    st.header("💬 Intelligent Assistant - Chat UI")
    st.markdown("Engage in seamless conversations powered by our AI-driven assistant.")

    # Initialize chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history.append({"role": "assistant", "content": "Hello! How can I assist you today?"})

    # Display the conversation using a modern chat layout
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input field for the user's query
    query = st.chat_input("Type your message")
    
    if query:
        # Append user's query to chat history
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        with st.spinner("Assistant is typing..."):
            headers = {"authorization-key": f"Bearer {st.session_state.get('token', '')}"}
            try:
                response = requests.post(
                    f"{BASE_URL}/helpers/llm-call",
                    json={"query": query},
                    headers=headers
                )
                if response.status_code == 200:
                    assistant_response = response.json().get("response", "No response")
                else:
                    assistant_response = "An error occurred while processing your request."
            except Exception:
                assistant_response = "An error occurred while processing your request."

        # Streaming response simulation
        def word_by_word(text):
            words = text.split()
            for i, word in enumerate(words):
                yield word + (" " if i < len(words)-1 else "")
                time.sleep(0.1)  # Simulate typing delay

        with st.chat_message("assistant"):
            streamed_text = st.write_stream(word_by_word(assistant_response))
        st.session_state.chat_history.append({"role": "assistant", "content": streamed_text})
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Navigation button
    if st.button("Back to Dashboard"):
        navigate_to("Dashboard")

def reasoning_model_ui():
    st.header("🧠 Advanced Reasoning Model")
    st.markdown("Enhance decision-making and analytical processes with AI.")

    query = st.text_area("Query:", "")
    expected_output = st.text_input("Expected Output:", "")
    additional_requirements = st.text_area("Additional Requirements:", "")

    if st.button("Analyze Query"):
        headers = {"authorization-key": f"Bearer {st.session_state.get('token', '')}"}
        payload = {
            "query": query,
            "expected_output": expected_output,
            "additional_requirements": additional_requirements
        }

        response = requests.post(f"{BASE_URL}/helpers/llm-call/reasoning-model", json=payload, headers=headers)

        if response.status_code == 200:
            st.markdown(f"**Response:** {response.json().get('final_response', 'No response')}")
        else:
            st.error("An error occurred while processing your request.")

    if st.button("Back to Dashboard"):
        navigate_to("Dashboard")

def agent_call_ui():
    st.header("🤖 AI-Powered Agent Interface")
    st.markdown("""
    Leverage AI agents for complex data retrieval and research insights.
    """)
    agent_type = st.selectbox("Select Agent Type", ["web-agent", "multi-agent"])
    query = st.text_area("Enter your query:")
    if st.button("Retrieve Insights"):
        headers = {"authorization-key": f"Bearer {st.session_state.get('token', '')}"}
        response = requests.post(f"{BASE_URL}/helpers/agent-call/{agent_type}", json={"query": query}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.markdown(f"**Answer:** {data.get('answer', 'No answer')}")
            if "results" in data:
                st.subheader("Additional Resources")
                for result in data["results"]:
                    st.markdown(f"- [{result['title']}]({result['url']}) - {result['snippet']}")
        else:
            st.error("An error occurred while processing your request.")
    if st.button("Back to Dashboard"):
        navigate_to("Dashboard")

def main():
    st.sidebar.title("🚀 Navigation")
    
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        generate_token()
    else:
        # Sidebar navigation with radio buttons
        modules = ["Dashboard", "Intelligent Assistant", "Advanced Reasoning", "AI-Powered Agent"]
        current_module = st.session_state.get("selected_module", "Dashboard")
        selected_module = st.sidebar.radio("Select a Module", modules, index=modules.index(current_module))
        if selected_module != current_module:
            navigate_to(selected_module)
        
        # Routing to the correct UI based on session state
        if st.session_state["selected_module"] == "Dashboard":
            main_menu()
        elif st.session_state["selected_module"] == "Intelligent Assistant":
            chat_ui()
        elif st.session_state["selected_module"] == "Advanced Reasoning":
            reasoning_model_ui()
        elif st.session_state["selected_module"] == "AI-Powered Agent":
            agent_call_ui()

if __name__ == "__main__":
    main()
