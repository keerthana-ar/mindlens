import streamlit as st
from emotion_model.classifier import get_top_emotion
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load prompts
with open("prompts/emotion_to_prompt.json", "r") as f:
    emotion_prompts = json.load(f)

def generate_reflection(emotion, text):
    prompt = emotion_prompts.get(emotion.lower(), "Provide a thoughtful response.")
    full_prompt = f"{prompt}\n\nUser's entry:\n{text}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.7
    )
    return response.choices[0].message["content"]

# --- Streamlit UI ---
st.set_page_config(page_title="MindLens", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
        .title {font-size: 36px; font-weight: 700; color: #4B8BBE;}
        .subtitle {font-size: 18px; color: #666; margin-bottom: 20px;}
        .footer {font-size: 12px; color: #999; margin-top: 40px;}
        .stTextArea textarea {background-color: #f4f4f4; font-size: 16px;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🧠 MindLens: AI Emotion Journal</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Write your thoughts. Let AI detect your emotions and gently reflect back.</div>", unsafe_allow_html=True)

user_input = st.text_area("What's on your mind today?", height=200, placeholder="Type your journal entry here...")

if st.button("🪄 Analyze My Emotion"):
    if user_input.strip() == "":
        st.warning("Please enter a journal entry to analyze.")
    else:
        emotion, score = get_top_emotion(user_input)
        st.success(f"\n\n**Emotion Detected:** {emotion.capitalize()} ({score}%)")

        reflection = generate_reflection(emotion, user_input)
        st.markdown("### 🧘 Reflection")
        st.markdown(f"<div style='background-color:#eef;border-radius:8px;padding:15px;'>{reflection}</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>Built with &#10084; by Keerthana</div>", unsafe_allow_html=True)

