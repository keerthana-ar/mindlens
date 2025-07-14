import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_emotion_classifier():
    """Load the emotion classification model with caching"""
    try:
        classifier = pipeline(
            "text-classification",
            model="bhadresh-savani/distilbert-base-uncased-emotion",
            return_all_scores=True
        )
        return classifier
    except Exception as e:
        st.error(f"Failed to load emotion model: {str(e)}")
        return None

def get_top_emotion(text):
    """Get the top emotion from text with error handling"""
    if not text or text.strip() == "":
        return "neutral", 0.0

    try:
        classifier = load_emotion_classifier()
        if classifier is None:
            return "neutral", 0.0

        results = classifier(text)[0]
        top_result = max(results, key=lambda x: x['score'])
        return top_result['label'], round(top_result['score'] * 100, 2)

    except Exception as e:
        st.error(f"Error analyzing emotion: {str(e)}")
        return "neutral", 0.0