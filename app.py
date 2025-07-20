import streamlit as st

# MUST BE FIRST - Set page config before any other Streamlit commands
st.set_page_config(
    page_title="MindLens - AI Emotion Journal", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules
from emotion_model.classifier import get_top_emotion
from backend.database import DatabaseManager
from backend.analytics import EmotionAnalytics
from backend.auth import AuthManager
from backend.utils import format_timestamp, get_emotion_color, get_emotion_emoji
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import time

load_dotenv()

# Initialize backend components
@st.cache_resource
def initialize_components():
    """Initialize all backend components with caching"""
    db = DatabaseManager()
    analytics = EmotionAnalytics(db)
    auth = AuthManager()
    return db, analytics, auth

# Initialize OpenAI client with error handling
@st.cache_resource
def initialize_openai_client():
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OpenAI API key not found. Please add it to your .env file."
        
        client = OpenAI(api_key=api_key, timeout=30.0)
        client.models.list()  # Test connection
        return client, None
        
    except Exception as e:
        return None, f"Failed to initialize OpenAI client: {str(e)}"

# Load prompts with error handling
@st.cache_data
def load_emotion_prompts():
    try:
        with open("prompts/emotion_to_prompt.json", "r") as f:
            return json.load(f), None
    except FileNotFoundError:
        return {}, "emotion_to_prompt.json file not found."
    except json.JSONDecodeError:
        return {}, "Invalid JSON in emotion_to_prompt.json file."

def generate_reflection(client, emotion_prompts, emotion, text, user_id):
    """Generate AI reflection with enhanced prompting"""
    try:
        base_prompt = emotion_prompts.get(emotion.lower(), "Provide a thoughtful response.")
        
        # Enhanced prompt with context
        full_prompt = f"""
        {base_prompt}
        
        Please provide a compassionate, personalized response that:
        1. Acknowledges the user's emotional state
        2. Offers practical coping strategies or positive reinforcement
        3. Encourages self-reflection and growth
        4. Keeps the tone warm and supportive
        
        User's journal entry:
        {text}
        
        Respond in 2-3 paragraphs, being empathetic and helpful.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I'm having trouble generating a reflection right now. Please try again later. Error: {str(e)}"

# Custom CSS for modern design
def load_custom_css():
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        .main {
            font-family: 'Inter', sans-serif;
        }
        
        /* Header Styles */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .main-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-subtitle {
            font-size: 1.2rem;
            font-weight: 300;
            opacity: 0.9;
        }
        
        /* Card Styles */
        .emotion-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
            margin: 1rem 0;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .emotion-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .reflection-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            border-left: 5px solid #4CAF50;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .journal-entry-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }
        
        .journal-entry-card:hover {
            box-shadow: 0 5px 25px rgba(0,0,0,0.12);
        }
        
        /* Emotion Badge */
        .emotion-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.9rem;
            margin: 0.5rem 0;
        }
        
        /* Stats Cards */
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
            margin: 0.5rem;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            font-weight: 500;
        }
        
        /* Button Styles */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        /* Text Area Styles */
        .stTextArea textarea {
            border-radius: 10px;
            border: 2px solid #e1e5e9;
            font-size: 1rem;
            padding: 1rem;
            transition: border-color 0.3s ease;
            font-family: 'Inter', sans-serif;
        }
        
        .stTextArea textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Sidebar Styles */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Loading Animation */
        .loading-animation {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Success Animation */
        .success-checkmark {
            color: #4CAF50;
            font-size: 2rem;
            animation: bounce 0.6s ease-in-out;
        }
        
        @keyframes bounce {
            0%, 20%, 60%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            80% { transform: translateY(-5px); }
        }
        
        /* Dark theme support */
        @media (prefers-color-scheme: dark) {
            .emotion-card, .journal-entry-card, .stat-card {
                background: #2d3748;
                color: white;
            }
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
            }
            .main-subtitle {
                font-size: 1rem;
            }
            .emotion-card, .reflection-card {
                padding: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the main header with modern design"""
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🧠 MindLens</div>
        <div class="main-subtitle">AI-Powered Emotion Journal & Mental Wellness Companion</div>
    </div>
    """, unsafe_allow_html=True)

def render_emotion_analysis(emotion, score, text, reflection):
    """Render emotion analysis results with beautiful cards"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        emoji = get_emotion_emoji(emotion)
        color = get_emotion_color(emotion)
        
        st.markdown(f"""
        <div class="emotion-card">
            <div style="text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{emoji}</div>
                <div class="emotion-badge" style="background-color: {color}; color: white;">
                    {emotion.upper()} - {score}%
                </div>
                <div style="margin-top: 1rem; color: #666; font-size: 0.9rem;">
                    Confidence Level: {"High" if score > 70 else "Medium" if score > 50 else "Low"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="reflection-card">
            <h3 style="color: #2c3e50; margin-bottom: 1rem;">🧘 AI Reflection</h3>
            <p style="line-height: 1.6; color: #34495e;">{reflection}</p>
        </div>
        """, unsafe_allow_html=True)

def render_journal_history(db, user_id):
    """Render journal history with search and filtering"""
    st.subheader("📖 Your Journal History")
    
    # Get entries
    entries = db.get_user_entries(user_id, limit=50)
    
    if not entries:
        st.info("No journal entries yet. Start writing to see your history!")
        return
    
    # Search and filter options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search your entries", placeholder="Search by content...")
    
    with col2:
        emotions = list(set([entry['emotion'] for entry in entries]))
        emotion_filter = st.selectbox("Filter by emotion", ["All"] + emotions)
    
    with col3:
        date_range = st.selectbox("Date range", ["All time", "Last 7 days", "Last 30 days"])
    
    # Filter entries
    filtered_entries = entries
    
    if search_term:
        filtered_entries = [e for e in filtered_entries if search_term.lower() in e['content'].lower()]
    
    if emotion_filter != "All":
        filtered_entries = [e for e in filtered_entries if e['emotion'] == emotion_filter]
    
    if date_range != "All time":
        days = 7 if date_range == "Last 7 days" else 30
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_entries = [e for e in filtered_entries if datetime.fromisoformat(e['timestamp']) > cutoff_date]
    
    # Display entries
    for entry in filtered_entries[:10]:  # Show latest 10
        emoji = get_emotion_emoji(entry['emotion'])
        color = get_emotion_color(entry['emotion'])
        
        st.markdown(f"""
        <div class="journal-entry-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span class="emotion-badge" style="background-color: {color}; color: white;">
                    {emoji} {entry['emotion'].upper()}
                </span>
                <span style="color: #666; font-size: 0.9rem;">
                    {format_timestamp(entry['timestamp'])}
                </span>
            </div>
            <p style="margin-bottom: 1rem; line-height: 1.5;">{entry['content'][:200]}{'...' if len(entry['content']) > 200 else ''}</p>
            {f'<div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; font-style: italic; color: #555;"><strong>Reflection:</strong> {entry["reflection"][:150]}{"..." if len(entry["reflection"]) > 150 else ""}</div>' if entry.get('reflection') else ''}
        </div>
        """, unsafe_allow_html=True)

def render_analytics_dashboard(analytics, user_id):
    """Render comprehensive analytics dashboard"""
    st.subheader("📊 Your Emotional Journey")
    
    # Get analytics data
    emotion_counts = analytics.get_emotion_distribution(user_id)
    mood_trends = analytics.get_mood_trends(user_id)
    weekly_stats = analytics.get_weekly_summary(user_id)
    
    if not emotion_counts:
        st.info("Write a few journal entries to see your emotional analytics!")
        return
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    total_entries = sum(emotion_counts.values())
    most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])
    avg_entries_per_week = weekly_stats.get('avg_entries_per_week', 0)
    streak_days = analytics.get_writing_streak(user_id)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_entries}</div>
            <div class="stat-label">Total Entries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        emoji = get_emotion_emoji(most_common_emotion[0])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{emoji}</div>
            <div class="stat-label">Most Common<br>{most_common_emotion[0].title()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{avg_entries_per_week:.1f}</div>
            <div class="stat-label">Avg Entries/Week</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{streak_days}</div>
            <div class="stat-label">Day Streak</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Emotion distribution pie chart
        if emotion_counts:
            fig_pie = px.pie(
                values=list(emotion_counts.values()),
                names=list(emotion_counts.keys()),
                title="Emotion Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(
                font=dict(family="Inter", size=12),
                title_font_size=16,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Mood trends over time
        if mood_trends:
            df_trends = pd.DataFrame(mood_trends)
            fig_line = px.line(
                df_trends, 
                x='date', 
                y='mood_score',
                title="Mood Trends Over Time",
                color_discrete_sequence=['#667eea']
            )
            fig_line.update_layout(
                font=dict(family="Inter", size=12),
                title_font_size=16,
                xaxis_title="Date",
                yaxis_title="Mood Score"
            )
            st.plotly_chart(fig_line, use_container_width=True)

def main():
    """Main application function"""
    # Load custom CSS
    load_custom_css()
    
    # Initialize components
    db, analytics, auth = initialize_components()
    client, client_error = initialize_openai_client()
    emotion_prompts, prompts_error = load_emotion_prompts()
    
    # Render header
    render_header()
    
    # Display any initialization errors
    if client_error:
        st.error(client_error)
        st.info("Please check your .env file and ensure your OpenAI API key is correctly set.")
        return
    
    if prompts_error:
        st.error(prompts_error)
        return
    
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = auth.get_or_create_user()
    
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Write"
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        tab = st.radio(
            "Choose a section:",
            ["✍️ Write", "📖 History", "📊 Analytics", "⚙️ Settings"],
            index=["✍️ Write", "📖 History", "📊 Analytics", "⚙️ Settings"].index(f"✍️ {st.session_state.current_tab}" if st.session_state.current_tab == "Write" else f"📖 {st.session_state.current_tab}" if st.session_state.current_tab == "History" else f"📊 {st.session_state.current_tab}" if st.session_state.current_tab == "Analytics" else f"⚙️ {st.session_state.current_tab}")
        )
        st.session_state.current_tab = tab.split(" ", 1)[1]
        
        # Quick stats in sidebar
        st.markdown("### 📈 Quick Stats")
        user_stats = analytics.get_user_stats(st.session_state.user_id)
        st.metric("Total Entries", user_stats.get('total_entries', 0))
        st.metric("This Week", user_stats.get('entries_this_week', 0))
        
        # Tips
        st.markdown("### 💡 Daily Tip")
        tips = [
            "Regular journaling can improve mental clarity and emotional awareness.",
            "Try writing for just 5 minutes each day to build a healthy habit.",
            "Notice patterns in your emotions to better understand your triggers.",
            "Use your reflections as a guide for personal growth and self-care."
        ]
        import random
        st.info(random.choice(tips))
    
    # Main content based on selected tab
    if st.session_state.current_tab == "Write":
        # Writing interface
        st.markdown("### ✍️ Express Your Thoughts")
        
        # Enhanced text area with character counter
        user_input = st.text_area(
            "What's on your mind today?",
            height=200,
            placeholder="Pour your heart out... I'm here to listen and reflect with you. 💙",
            max_chars=2000,
            help="Write freely about your thoughts, feelings, or experiences. The AI will analyze your emotions and provide thoughtful reflections."
        )
        
        # Character counter
        if user_input:
            char_count = len(user_input)
            st.caption(f"Characters: {char_count}/2000")
        
        # Real-time emotion detection toggle
        real_time = st.checkbox("🔄 Real-time emotion detection", help="Get live emotion analysis as you type")
        
        if real_time and user_input and len(user_input) > 50:
            with st.spinner("Analyzing emotions..."):
                emotion, score = get_top_emotion(user_input)
                emoji = get_emotion_emoji(emotion)
                st.info(f"Current emotion: {emoji} {emotion.title()} ({score}%)")
        
        # Analysis button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button("🪄 Analyze My Emotions & Get Reflection", use_container_width=True)
        
        if analyze_button:
            if not user_input or user_input.strip() == "":
                st.warning("Please share your thoughts first! ✨")
            elif len(user_input.strip()) < 10:
                st.warning("Please write a bit more so I can better understand your emotions. 💭")
            else:
                # Show loading animation
                with st.spinner("🧠 Analyzing your emotions and crafting a personalized reflection..."):
                    progress_bar = st.progress(0)
                    
                    # Emotion analysis
                    progress_bar.progress(25)
                    emotion, score = get_top_emotion(user_input)
                    
                    # Generate reflection
                    progress_bar.progress(50)
                    reflection = generate_reflection(client, emotion_prompts, emotion, user_input, st.session_state.user_id)
                    
                    # Save to database
                    progress_bar.progress(75)
                    entry_id = db.save_entry(st.session_state.user_id, user_input, emotion, score, reflection)
                    
                    progress_bar.progress(100)
                    time.sleep(0.5)  # Brief pause for effect
                    progress_bar.empty()
                
                # Show success animation
                st.markdown('<div class="success-checkmark">✅ Analysis Complete!</div>', unsafe_allow_html=True)
                
                # Render results
                render_emotion_analysis(emotion, score, user_input, reflection)
                
                # Clear the text area for next entry
                if st.button("✨ Start New Entry"):
                    st.rerun()
    
    elif st.session_state.current_tab == "History":
        render_journal_history(db, st.session_state.user_id)
    
    elif st.session_state.current_tab == "Analytics":
        render_analytics_dashboard(analytics, st.session_state.user_id)
    
    elif st.session_state.current_tab == "Settings":
        st.subheader("⚙️ Settings & Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎨 Appearance")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            
            st.markdown("#### 🔔 Notifications")
            daily_reminder = st.checkbox("Daily writing reminder")
            if daily_reminder:
                reminder_time = st.time_input("Reminder time")
            
            st.markdown("#### 📊 Privacy")
            anonymous_mode = st.checkbox("Anonymous mode")
            data_retention = st.selectbox("Data retention", ["1 month", "6 months", "1 year", "Forever"])
        
        with col2:
            st.markdown("#### 📤 Export Data")
            if st.button("Export Journal Entries"):
                # TODO: Implement export functionality
                st.success("Export feature coming soon!")
            
            st.markdown("#### 🗑️ Data Management")
            if st.button("Clear All Data", type="secondary"):
                if st.checkbox("I understand this will delete all my data"):
                    # TODO: Implement data clearing
                    st.warning("Data clearing feature coming soon!")
            
            st.markdown("#### ℹ️ About")
            st.info("""
            **MindLens v2.0**
            
            An AI-powered emotional wellness companion that helps you understand and reflect on your feelings through intelligent journaling.
            
            Built with ❤️ by Keerthana
            """)

if __name__ == "__main__":
    main()