# 🧠 Fake Comment Detector

A web-based machine learning application that classifies user comments as **fake** or **genuine** using Natural Language Processing (NLP). This project demonstrates the full ML pipeline from text preprocessing and vectorization to model deployment in a Flask web app.

---

## 🚀 Features

- ✅ Classifies comments as **real** or **fake**
- ✅ Pre-trained ML model using **TF-IDF vectorization**
- ✅ Lightweight and interactive **Flask web interface**
- ✅ Simple HTML frontend for user input
- ✅ Easily extendable for new datasets or models

---

## 🧠 Technologies Used

- **Python 3**
- **Flask**
- **Scikit-learn**
- **Pickle** for model serialization
- **HTML / Jinja2 templates**

---

## 🧪 Model Overview

The model was trained on a labeled dataset of user comments. The comments were vectorized using a **TF-IDF Vectorizer** and fed into a classification algorithm (e.g., Logistic Regression or SVM). The trained model and vectorizer were saved using Pickle for deployment.

> 🔒 Note: Training code and dataset are not included in this repository. You can add your own dataset and training script for full reproducibility.

---

## 📁 Project Structure
fake-comment-detector/
│
├── app.py # Main Flask application
├── vectorizer.pkl # Trained TF-IDF vectorizer
├── fake_comment_detector.pkl # Trained ML classifier
├── templates/
│ └── index.html # Frontend for user input
