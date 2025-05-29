from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sys

try:
    analyzer = SentimentIntensityAnalyzer()
    print("VADER Sentiment Analyzer initialized successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize VADER Sentiment Analyzer: {e}", file=sys.stderr)
    analyzer = None # Allow app to run, but sentiment will be neutral

def get_sentiment(text):
    if not analyzer or not isinstance(text, str):
        print("Warning: VADER analyzer not available or invalid text provided for sentiment.")
        return {'score': 0.0, 'label': 'neutral'} # Default

    try:
        vs = analyzer.polarity_scores(text)
        score = vs['compound']
        label = 'neutral'
        if score >= 0.05: label = 'positive'
        elif score <= -0.05: label = 'negative'
        print(f"Sentiment calculated: Label={label}, Score={score:.2f}")
        return {'score': score, 'label': label}
    except Exception as e:
        print(f"Warning: VADER sentiment analysis failed for text '{text[:50]}...': {e}")
        return {'score': 0.0, 'label': 'neutral'}