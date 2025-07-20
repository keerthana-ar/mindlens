import streamlit as st
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

@st.cache_resource
def load_emotion_classifier():
    """Load the emotion classification model with caching"""
    try:
        # Try to use a simpler, more compatible model first
        classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
        return classifier
    except Exception as e:
        try:
            # Fallback to a different model
            classifier = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-emotion",
                return_all_scores=True
            )
            return classifier
        except Exception as e2:
            st.error(f"Failed to load emotion model: {str(e2)}")
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
        
        # Map different model labels to our standard emotions
        emotion_mapping = {
            'LABEL_0': 'sadness', 'LABEL_1': 'joy', 'LABEL_2': 'love',
            'LABEL_3': 'anger', 'LABEL_4': 'fear', 'LABEL_5': 'surprise',
            'sadness': 'sadness', 'joy': 'joy', 'love': 'love',
            'anger': 'anger', 'fear': 'fear', 'surprise': 'surprise',
            'optimism': 'joy', 'pessimism': 'sadness'
        }
        
        emotion = emotion_mapping.get(top_result['label'].lower(), top_result['label'].lower())
        return emotion, round(top_result['score'] * 100, 2)

    except Exception as e:
        st.error(f"Error analyzing emotion: {str(e)}")
        return "neutral", 0.0