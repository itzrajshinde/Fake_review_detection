
from flask import Flask, request, jsonify, render_template
import os
import sys
import traceback
import joblib  # For loading the model
import numpy as np # For handling prediction probabilities

try:
    from .analyzer import get_sentiment
except ImportError as e:
     print(f"ERROR: Failed to import analyzer module. Details: {e}", file=sys.stderr)
     def get_sentiment(text): return {'score': 0.0, 'label': 'neutral'}
     print("WARNING: Sentiment analysis will default to neutral.", file=sys.stderr)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
MODEL_FILENAME = 'fake_comment_classifier.joblib'
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
pipeline = None # Global variable for the loaded model pipeline
model_loaded_successfully = False # Flag to pass to template

try:
    print(f"Attempting to load model pipeline from: {MODEL_PATH}")
    if os.path.exists(MODEL_PATH):
        pipeline = joblib.load(MODEL_PATH) # This loads the model
        print("ML Model pipeline loaded successfully.")
        try:
            _ = pipeline.predict_proba(["test comment"])
            print("Model prediction test successful.")
            model_loaded_successfully = True # Set flag on success
        except Exception as load_pred_e:
             print(f"WARNING: Model loaded but test prediction failed: {load_pred_e}", file=sys.stderr)
             model_loaded_successfully = True # Or set to False if test MUST pass
    else:
        print(f"ERROR: Model file '{MODEL_PATH}' not found.", file=sys.stderr)
        print("Please run 'python train_model.py' first to train and save the model.", file=sys.stderr)
except Exception as e:
    print(f"ERROR: Failed to load the model pipeline from '{MODEL_PATH}'. Error: {e}", file=sys.stderr)
    traceback.print_exc()

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    if not os.path.isdir(template_dir): print(f"WARNING: Template directory missing.", file=sys.stderr)
    if not os.path.isdir(static_dir): print(f"WARNING: Static directory missing.", file=sys.stderr)
except Exception as path_e:
     print(f"ERROR setting up paths: {path_e}", file=sys.stderr); sys.exit(1)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


@app.route('/')
def index():
    print(f"Rendering index page. Model loaded status: {model_loaded_successfully}")
    return render_template('index.html', model_loaded=model_loaded_successfully)

@app.route('/analyze_comment', methods=['POST'])
def analyze_single_comment():
    print("\nReceived request for /analyze_comment")
    if not model_loaded_successfully or pipeline is None:
        print("Error: Model not loaded or unavailable, cannot analyze.", file=sys.stderr)
        return jsonify({"error": "Analysis model is currently unavailable. Please check server status or try again later."}), 503 # Service Unavailable

    if not request.is_json:
        print("Error: Request Content-Type is not application/json", file=sys.stderr)
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.get_json()
    print(f"Request data: {data}")
    comment_text = data.get('text')

    if not comment_text or not isinstance(comment_text, str) or not comment_text.strip():
         print("Error: Comment text is missing or empty in request.", file=sys.stderr)
         return jsonify({"error": "Comment text is missing or empty"}), 400

    try:
        input_text = [comment_text]

        prediction_proba = pipeline.predict_proba(input_text)[0]

        predicted_class = np.argmax(prediction_proba)

        verdict = 'fake' if predicted_class == 1 else 'genuine'

        confidence = prediction_proba[predicted_class] * 100

        print(f"Prediction: {verdict} (Class={predicted_class}), Confidence: {confidence:.2f}%")
        print(f"Probabilities: [Real={prediction_proba[0]:.4f}, Fake={prediction_proba[1]:.4f}]")

        sentiment_result = get_sentiment(comment_text)
        print(f"Sentiment: {sentiment_result['label']} (Score: {sentiment_result['score']:.2f})")

        return jsonify({
            "verdict": verdict,
            "confidence": round(confidence, 1), # Rounded confidence percentage
            "sentiment": sentiment_result['label'],
            "error": None # Explicitly indicate no error
        }), 200

    except Exception as e:
        print(f"ERROR during ML prediction or sentiment analysis: {e}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred during analysis."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)