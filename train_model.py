# File: train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
import joblib
import os
import sys

# --- Configuration ---
# !!! IMPORTANT: UPDATE THESE VALUES !!!
CSV_FILE_PATH = 'fake reviews dataset.csv' # <--- SET THE ACTUAL PATH TO YOUR CSV FILE
TEXT_COLUMN = 'text_'                          # <--- SET THE NAME OF THE TEXT COLUMN IN YOUR CSV
LABEL_COLUMN = 'label'                        # <--- SET THE NAME OF THE LABEL COLUMN (fake/real)
# Define what value represents 'fake' in your label column
# Examples: 1, 'FAKE', 'fake', True
FAKE_LABEL_VALUE = 'CG'                         # <--- ADJUST IF NEEDED (e.g., 'FAKE')

# --- Output ---
MODEL_DIR = 'app/models' # Directory to save models (relative to this script)
MODEL_FILENAME = 'fake_comment_classifier.joblib'
# -------------------

def train():
    """Loads data, trains classifier, and saves the pipeline."""

    print("--- Starting Model Training ---")

    # 1. Load Data
    print(f"Loading data from: {CSV_FILE_PATH}")
    if not os.path.exists(CSV_FILE_PATH):
        print(f"ERROR: CSV file not found at '{CSV_FILE_PATH}'. Update path in train_model.py.", file=sys.stderr)
        sys.exit(1)
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Loaded {len(df)} rows.")
    except Exception as e:
        print(f"ERROR: Failed to load CSV. Error: {e}", file=sys.stderr); sys.exit(1)

    if TEXT_COLUMN not in df.columns:
        print(f"ERROR: Text column '{TEXT_COLUMN}' not found. Available: {df.columns.tolist()}", file=sys.stderr); sys.exit(1)
    if LABEL_COLUMN not in df.columns:
        print(f"ERROR: Label column '{LABEL_COLUMN}' not found. Available: {df.columns.tolist()}", file=sys.stderr); sys.exit(1)

    # Handle missing text data
    initial_rows = len(df)
    df.dropna(subset=[TEXT_COLUMN], inplace=True)
    df[TEXT_COLUMN] = df[TEXT_COLUMN].astype(str) # Ensure text is string
    if len(df) < initial_rows:
        print(f"Dropped {initial_rows - len(df)} rows with missing text.")
    print(f"Using {len(df)} rows for training.")
    if len(df) == 0: print("ERROR: No data left after handling missing text.", file=sys.stderr); sys.exit(1)


    print(f"Preparing labels from '{LABEL_COLUMN}' (Fake = '{FAKE_LABEL_VALUE}')...")
    try:
        label_type = df[LABEL_COLUMN].dtype
        compare_value = FAKE_LABEL_VALUE
        if pd.api.types.is_string_dtype(label_type):
            compare_value = str(FAKE_LABEL_VALUE)
            # Make comparison case-insensitive if labels are strings
            df['label_binary'] = df[LABEL_COLUMN].astype(str).str.strip().str.upper() == compare_value.upper()
        elif pd.api.types.is_bool_dtype(label_type):
             compare_value = bool(FAKE_LABEL_VALUE)
             df['label_binary'] = df[LABEL_COLUMN] == compare_value
        else: # Assume numeric or can be coerced
             compare_value = int(FAKE_LABEL_VALUE)
             df['label_binary'] = pd.to_numeric(df[LABEL_COLUMN], errors='coerce') == compare_value

        df['label_binary'] = df['label_binary'].astype(int) # Ensure 0 or 1

        print("Label distribution (0=Real, 1=Fake):")
        print(df['label_binary'].value_counts(normalize=True))
        if df['label_binary'].nunique() < 2:
             print("WARNING: Only one class found in labels after conversion. Model may not train well.", file=sys.stderr)

    except Exception as e:
        print(f"ERROR: Failed converting labels. Check LABEL_COLUMN & FAKE_LABEL_VALUE. Error: {e}", file=sys.stderr); sys.exit(1)

    X = df[TEXT_COLUMN]
    y = df['label_binary']

    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        print(f"Data split: Train={len(X_train)}, Test={len(X_test)}")
    except ValueError as e:
         print(f"WARNING: Could not stratify split (likely too few samples of one class). Splitting without stratify. Error: {e}", file=sys.stderr)
         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    print("Creating pipeline: TF-IDF(max_features=5000, ngram=(1,2)) -> LogisticRegression(balanced)")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1, 2))),
        ('clf', LogisticRegression(solver='liblinear', random_state=42, class_weight='balanced', C=1.0)) # C=1.0 is default regularization
    ])
    print("Training model...")
    pipeline.fit(X_train, y_train)
    print("Training complete.")

    print("\n--- Evaluating Model on Test Set ---")
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Real (0)', 'Fake (1)']))

    # 7. Save the Pipeline
    print("\n--- Saving Pipeline ---")
    os.makedirs(MODEL_DIR, exist_ok=True) # Ensure directory exists
    model_path = os.path.join(MODEL_DIR, MODEL_FILENAME)
    try:
        joblib.dump(pipeline, model_path)
        print(f"Pipeline saved successfully to: {model_path}")
    except Exception as e:
        print(f"ERROR: Failed to save pipeline. Error: {e}", file=sys.stderr); sys.exit(1)

    print("\n--- Training Script Finished ---")

if __name__ == "__main__":
    train()