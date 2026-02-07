"""
Streamlit web interface for the podcast chatbot.

Run with: streamlit run web.py
Or with custom port: streamlit run web.py --server.port 5000
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from chatbot import PodcastChatbot

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🎙️ Podbotnik - Podcast Chatbot",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 0.5rem;
    }
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
    .source-box {
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
    }
    .answer-box {
        border-radius: 0.5rem;
        padding: 1.5rem;
        background-color: #f0f4ff;
        margin: 1rem 0;
    }
    .episode-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        background-color: #667eea;
        color: white;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem 0.5rem 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
    st.session_state.transcript_file = None
    st.session_state.chat_history = []


def initialize_chatbot(transcript_file):
    """Initialize the chatbot with a transcript file."""
    try:
        chatbot = PodcastChatbot()
        chatbot.load_transcripts(transcript_file)
        return chatbot
    except Exception as e:
        st.error(f"❌ Error loading transcripts: {e}")
        return None



def main():
    """Main Streamlit app."""
    # Header
    st.markdown("# 🎙️ Podbotnik - Podcast Chatbot")
    st.markdown("Ask natural-language questions about your podcast episodes!")

    # Sidebar for configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Transcript file selector
        transcript_file = st.selectbox(
            "📁 Select Transcript File",
            options=[f for f in os.listdir(".") if f.endswith(".json")],
            index=0 if "sample_transcripts.json" in os.listdir(".") else None,
        )
        
        # Initialize chatbot button
        if st.button("🚀 Load Transcripts", use_container_width=True):
            if transcript_file:
                with st.spinner("Loading transcripts..."):
                    st.session_state.chatbot = initialize_chatbot(transcript_file)
                    st.session_state.transcript_file = transcript_file
                    st.session_state.chat_history = []
                if st.session_state.chatbot:
                    st.success("✅ Transcripts loaded successfully!")
            else:
                st.warning("Please select a transcript file")
        
        # Settings
        st.markdown("---")
        st.markdown("## 🎛️ Settings")
        max_context_segments = st.slider(
            "Max Context Segments",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of transcript segments to use for context"
        )
        
        # Display loaded episodes
        if st.session_state.chatbot:
            st.markdown("---")
            st.markdown("## 📊 Loaded Episodes")
            episodes = st.session_state.chatbot.list_episodes()
            st.markdown(f"**Total Episodes:** {len(episodes)}")
            
            if episodes:
                with st.expander(f"Show all {len(episodes)} episodes"):
                    for ep_id, ep_data in sorted(episodes.items(), 
                                                 key=lambda x: x[1].get("episode_number", 0)):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{ep_data.get('episode_title', 'Untitled')}**")
                            st.caption(f"ID: {ep_id}")
                        with col2:
                            st.markdown(f"Ep. {ep_data.get('episode_number', '?')}")

    # Main content area
    if not st.session_state.chatbot:
        st.info("👈 Load a transcript file from the sidebar to get started!")
        st.markdown("""
        ### How it works:
        1. Select a transcript JSON file
        2. Click "Load Transcripts"
        3. Ask questions about the podcast content
        4. Get answers with sources and timestamps
        """)
    else:
        # Chat interface
        st.markdown("### 💬 Ask a Question")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input(
                "Your question:",
                placeholder="e.g., What is machine learning?",
                label_visibility="collapsed"
            )
        with col2:
            ask_button = st.button("Ask", use_container_width=True, type="primary")
        
        if ask_button and question:
            with st.spinner("🤖 Generating answer..."):
                try:
                    result = st.session_state.chatbot.answer_question(
                        question,
                        max_context_segments=max_context_segments
                    )
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": question,
                        "result": result
                    })
                    
                    # Display answer
                    st.markdown("---")
                    st.markdown("### 🤖 Answer")
                    st.markdown(f"<div class='answer-box'>{result['answer']}</div>", 
                              unsafe_allow_html=True)
                    
                    # Display sources
                    if result.get("sources"):
                        st.markdown("### 📍 Sources")
                        for i, source in enumerate(result["sources"], 1):
                            with st.container():
                                st.markdown(f"""
                                <div class='source-box'>
                                <strong>📺 {source.get('episode_title', 'Unknown Episode')}</strong>
                                """, unsafe_allow_html=True)
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.caption(f"Episode #{source.get('episode_number', '?')}")
                                with col2:
                                    if source.get('timestamp'):
                                        st.caption(f"⏱️ {source['timestamp']}")
                                with col3:
                                    if source.get('video_link'):
                                        st.markdown(f"[🎬 Watch]({source['video_link']})")
                                
                                st.caption(source.get('text', '')[:200] + "...")
                                st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display context used
                    if result.get("context_used"):
                        with st.expander("📋 Context Used"):
                            for i, segment in enumerate(result["context_used"], 1):
                                st.markdown(f"**Segment {i}:**")
                                st.caption(segment)
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 📜 Chat History")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history), 1):
                with st.expander(f"Q{len(st.session_state.chat_history) - i + 1}: {chat['question'][:60]}..."):
                    st.markdown(f"**Question:** {chat['question']}")
                    st.markdown(f"**Answer:** {chat['result']['answer']}")
                    
                    if chat['result'].get('sources'):
                        st.markdown(f"**Sources:** {len(chat['result']['sources'])} found")
            
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()



if __name__ == "__main__":
    main()
    