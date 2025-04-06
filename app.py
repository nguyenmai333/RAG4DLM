import streamlit as st
from utils.llm import LLM  # Your custom LLM class
from dotenv import load_dotenv
import os

# If you're getting torch.classes.__path__ error:
import torch
torch.classes.__path__ = []  # Optional fix for specific torch issues

load_dotenv()  # Load environment variables (e.g., OPENAI_API_KEY)

# Page config
st.set_page_config(
    page_title="BKU Chat",
    layout="wide",
    page_icon="💬",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling
st.markdown("""
    <style>
        .title { font-size: 42px; font-weight: bold; color: #1E88E5; text-align: center; margin-bottom: 20px; }
        .user-message { color:black; background-color: #E3F2FD; border-radius: 10px; padding: 15px; margin: 5px 0; text-align: right; }
        .bot-message { color:black; background-color: #F5F5F5; border-radius: 10px; padding: 15px; margin: 5px 0; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Display chat history
def display_chat_messages():
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            class_name = 'user-message' if message["role"] == "user" else 'bot-message'
            sender = "You" if message["role"] == "user" else "Assistant"
            st.markdown(f"<div class='{class_name}'><b>{sender}:</b> {message['content']}</div>", 
                       unsafe_allow_html=True)

# Main app
def main():
    initialize_session_state()

    st.markdown("<div class='title'>BKU Chat</div>", unsafe_allow_html=True)
    st.markdown("##### Chat with Tung tung tung sahur")

    display_chat_messages()

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask a question:", placeholder="Type your question here...")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            with st.spinner("Generating response..."):
                llm = LLM(
                    model_name="gpt-4o-mini",  # Use correct model name
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                message_placeholder = st.empty()
                full_response = ""

                for chunk in llm.streaming_answer(user_input):
                    full_response += chunk or ""
                    message_placeholder.markdown(
                        f"<div class='bot-message'><b>Assistant:</b> {full_response}</div>", 
                        unsafe_allow_html=True
                    )
        except Exception as e:
            full_response = f"❌ Error: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

    if st.session_state.messages:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()
