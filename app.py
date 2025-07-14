import streamlit as st

# MUST BE FIRST - Set page config before any other Streamlit commands
st.set_page_config(page_title="MindLens", page_icon="🧠", layout="centered")

# Now import other modules
from emotion_model.classifier import get_top_emotion
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client with error handling
def initialize_openai_client():
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OpenAI API key not found. Please add it to your .env file."
        
        # Initialize client with explicit parameters only
        client = OpenAI(
            api_key=api_key,
            timeout=30.0,  # Add timeout
        )
        
        # Test the client connection
        client.models.list()
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

def generate_reflection(client, emotion_prompts, emotion, text):
    try:
        prompt = emotion_prompts.get(emotion.lower(), "Provide a thoughtful response.")
        full_prompt = f"{prompt}\n\nUser's entry:\n{text}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=500  # Add token limit
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Failed to generate reflection: {str(e)}"

# Initialize components
client, client_error = initialize_openai_client()
emotion_prompts, prompts_error = load_emotion_prompts()

# Safe CSS styling
st.markdown("""
    <style>
        .title {font-size: 36px; font-weight: 700; color: #4B8BBE;}
        .subtitle {font-size: 18px; color: #666; margin-bottom: 20px;}
        .footer {font-size: 12px; color: #999; margin-top: 40px;}
        .stTextArea textarea {background-color: #f4f4f4; font-size: 16px;}
        .reflection-box {
            background-color: #eef; 
            border-radius: 8px; 
            padding: 15px; 
            border-left: 4px solid #4B8BBE;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🧠 MindLens: AI Emotion Journal</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Write your thoughts. Let AI detect your emotions and gently reflect back.</div>", unsafe_allow_html=True)

# Display any initialization errors
if client_error:
    st.error(client_error)
    st.info("Please check your .env file and ensure your OpenAI API key is correctly set.")
    st.stop()

if prompts_error:
    st.error(prompts_error)
    st.stop()

user_input = st.text_area(
    "What's on your mind today?", 
    height=200, 
    placeholder="Type your journal entry here...",
    max_chars=1000  # Add character limit
)

if st.button("🪄 Analyze My Emotion"):
    if not user_input or user_input.strip() == "":
        st.warning("Please enter a journal entry to analyze.")
    else:
        with st.spinner("Analyzing your emotion..."):
            try:
                emotion, score = get_top_emotion(user_input)
                st.success(f"**Emotion Detected:** {emotion.capitalize()} ({score}%)")

                with st.spinner("Generating reflection..."):
                    reflection = generate_reflection(client, emotion_prompts, emotion, user_input)
                    st.markdown("### 🧘 Reflection")
                    st.markdown(f"<div class='reflection-box'>{reflection}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

st.markdown("<div class='footer'>Built with &#10084; by Keerthana</div>", unsafe_allow_html=True)