"""
Streamlit Frontend for NLP Comment Processor
Provides user interface for uploading comments and viewing analysis results
"""

import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="NLP Comment Processor",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_URL = st.sidebar.text_input("API URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #6c5ce7;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stats-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #6c5ce7;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🎮 NLP Comment Processor</p>', unsafe_allow_html=True)
st.markdown("**Cross-Cultural Game Review Analysis System**")
st.markdown("---")


def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Home", "Upload & Process", "View Results", "Statistics", "Database"])
    
    st.markdown("---")
    st.subheader("API Status")
    if check_api_health():
        st.success("✅ Connected")
    else:
        st.error("❌ API Unavailable")
        st.info(f"Make sure FastAPI is running at {API_URL}")


# Page: Home
if page == "Home":
    st.header("Welcome to NLP Comment Processor")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Features")
        st.markdown("""
        - Multi-language support
        - Sentiment analysis
        - Topic clustering
        - Cross-cultural insights
        - LLM enhancement
        """)
    
    with col2:
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. Start FastAPI backend
        2. Upload comment data
        3. Process with NLP
        4. View analysis results
        5. Generate reports
        """)
    
    with col3:
        st.markdown("### 🔧 Tech Stack")
        st.markdown("""
        - Streamlit (Frontend)
        - FastAPI (Backend)
        - SQLAlchemy (ORM)
        - PostgreSQL/SQLite
        - Transformers (NLP)
        """)
    
    st.markdown("---")
    st.info("💡 **Tip**: Make sure the FastAPI backend is running before uploading data.")


# Page: Upload & Process
elif page == "Upload & Process":
    st.header("📤 Upload & Process Comments")
    
    tab1, tab2 = st.tabs(["Text Input", "File Upload"])
    
    with tab1:
        st.subheader("Enter Comments Manually")
        
        col1, col2 = st.columns(2)
        with col1:
            source = st.text_input("Source (Game Name)", "test_game")
        with col2:
            language = st.selectbox("Language", ["chinese", "japanese", "english", "korean"])
        
        comments_text = st.text_area(
            "Enter comments (one per line)",
            height=300,
            placeholder="Enter your comments here...\nOne comment per line"
        )
        
        if st.button("🚀 Process Comments", type="primary"):
            if comments_text:
                comments = [c.strip() for c in comments_text.split('\n') if c.strip()]
                
                with st.spinner("Processing comments..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/api/process/",
                            json={
                                "comments": comments,
                                "source": source,
                                "language": language
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Processing started! Job ID: {result['job_id']}")
                            st.info("Check the 'View Results' page to see progress.")
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Failed to connect to API: {e}")
            else:
                st.warning("⚠️ Please enter some comments first!")
    
    with tab2:
        st.subheader("Upload JSON File")
        st.info("Upload a JSON file containing comment data")
        
        uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])
        
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
                st.success(f"✅ File loaded: {len(data)} items")
                
                if st.button("🚀 Process Uploaded Data", type="primary"):
                    st.info("Processing functionality coming soon...")
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")


# Page: View Results
elif page == "View Results":
    st.header("📊 Analysis Results")
    
    tab1, tab2, tab3 = st.tabs(["Reviews", "Sentiment", "Topics"])
    
    with tab1:
        st.subheader("Reviews")
        try:
            response = requests.get(f"{API_URL}/api/reviews/")
            if response.status_code == 200:
                reviews = response.json()
                if reviews:
                    df = pd.DataFrame(reviews)
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total reviews: {len(reviews)}")
                else:
                    st.info("No reviews found in database")
            else:
                st.error("Failed to fetch reviews")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Sentiment Analysis Results")
        try:
            response = requests.get(f"{API_URL}/api/sentiment/")
            if response.status_code == 200:
                sentiments = response.json()
                if sentiments:
                    df = pd.DataFrame(sentiments)
                    st.dataframe(df, use_container_width=True)
                    
                    # Show distribution
                    if 'sentiment_label' in df.columns:
                        st.subheader("Sentiment Distribution")
                        sentiment_counts = df['sentiment_label'].value_counts()
                        st.bar_chart(sentiment_counts)
                else:
                    st.info("No sentiment results found")
            else:
                st.error("Failed to fetch sentiment results")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("Topic Clustering Results")
        try:
            response = requests.get(f"{API_URL}/api/topics/")
            if response.status_code == 200:
                topics = response.json()
                if topics:
                    df = pd.DataFrame(topics)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No topic results found")
            else:
                st.error("Failed to fetch topic results")
        except Exception as e:
            st.error(f"Error: {e}")


# Page: Statistics
elif page == "Statistics":
    st.header("📈 Statistics Dashboard")
    
    try:
        response = requests.get(f"{API_URL}/api/stats/overview")
        if response.status_code == 200:
            stats = response.json()
            
            # Display key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="stats-card">', unsafe_allow_html=True)
                st.metric("Total Reviews", stats['total_reviews'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="stats-card">', unsafe_allow_html=True)
                st.metric("Sentiment Results", stats['total_sentiments'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="stats-card">', unsafe_allow_html=True)
                st.metric("Topic Results", stats['total_topics'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Sentiment distribution chart
            st.subheader("Sentiment Distribution")
            sentiment_dist = stats['sentiment_distribution']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("😊 Positive", sentiment_dist['positive'])
            with col2:
                st.metric("😐 Neutral", sentiment_dist['neutral'])
            with col3:
                st.metric("😞 Negative", sentiment_dist['negative'])
            
            # Create chart data
            chart_data = pd.DataFrame({
                'Sentiment': ['Positive', 'Neutral', 'Negative'],
                'Count': [
                    sentiment_dist['positive'],
                    sentiment_dist['neutral'],
                    sentiment_dist['negative']
                ]
            })
            st.bar_chart(chart_data.set_index('Sentiment'))
            
        else:
            st.error("Failed to fetch statistics")
    except Exception as e:
        st.error(f"Error: {e}")


# Page: Database
elif page == "Database":
    st.header("🗄️ Database Management")
    
    st.warning("⚠️ Database operations can modify or delete data. Use with caution!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Database Info")
        if st.button("📊 Show Tables"):
            st.info("Tables: reviews, sentiment_results, topic_results")
    
    with col2:
        st.subheader("Maintenance")
        if st.button("🧹 Clear All Data", type="secondary"):
            st.warning("This would clear all data (not implemented in demo)")


# Footer
st.markdown("---")
st.markdown("**NLP Comment Processor** | Version 1.0.0 | FastAPI + Streamlit Architecture")
