from transformers import pipeline

classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", return_all_scores=True)

def get_top_emotion(text):
    results = classifier(text)[0]
    top_result = max(results, key=lambda x: x['score'])
    return top_result['label'], round(top_result['score'] * 100, 2)