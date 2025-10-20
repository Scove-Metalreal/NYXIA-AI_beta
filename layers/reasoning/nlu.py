from transformers import pipeline
from typing import Dict, Any

class NLUAnalyzer:
    def __init__(self):
        # Initialize a sentiment analysis pipeline from Hugging Face Transformers
        # This model is good for general sentiment (positive/negative)
        self.sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        # You can add more specialized pipelines here for emotion detection, intent, etc.
        # e.g., self.emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyzes the input text for sentiment and potentially other NLU features."""
        results = {
            "sentiment": {"label": "neutral", "score": 0.0}
        }

        # Sentiment Analysis
        sentiment_raw = self.sentiment_pipeline(text)[0]
        results["sentiment"]["label"] = sentiment_raw["label"].lower()
        results["sentiment"]["score"] = sentiment_raw["score"]

        # Convert sentiment score to a more usable range (e.g., -1 to 1)
        if results["sentiment"]["label"] == "negative":
            results["sentiment"]["score"] *= -1

        # Placeholder for more advanced emotion/intent detection
        # if self.emotion_pipeline:
        #     emotion_raw = self.emotion_pipeline(text)[0]
        #     results["emotion"] = {"label": emotion_raw["label"].lower(), "score": emotion_raw["score"]}

        return results

