"""
CodeAlpha Task 4: Sentiment Analysis
Train a TF-IDF + Logistic Regression model on labelled Amazon reviews.
"""

from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).parent / "sentiment_model.joblib"


def predict_sentiment(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    model = joblib.load(MODEL_PATH)
    positive_probability = float(model.predict_proba([text])[0, 1])

    if positive_probability >= 0.55:
        sentiment = "Positive"
    elif positive_probability <= 0.45:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "text": text,
        "sentiment": sentiment,
        "positive_probability": round(positive_probability, 4),
    }


if __name__ == "__main__":
    examples = [
        "The product is excellent and works perfectly.",
        "It is okay, neither great nor terrible.",
        "The battery is poor and the device stopped working.",
    ]
    for example in examples:
        print(predict_sentiment(example))
