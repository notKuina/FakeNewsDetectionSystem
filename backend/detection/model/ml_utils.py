import os
import csv
import joblib
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from django.conf import settings
from nltk.corpus import stopwords
import traceback

# --- Paths Configuration ---
MODEL_PATH = os.path.join(settings.BASE_DIR, 'detection', 'model', 'lr_model.jb')
VECTORIZER_PATH = os.path.join(settings.BASE_DIR, 'detection', 'model', 'vectorizer.jb')
DATA_DIR = os.path.join(settings.BASE_DIR, 'detection', 'data')

# --- Global Variables ---
model = None
vectorizer = None
dataset_df = None
dataset_vectors = None

# --- Preprocessing Function ---
def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)  # keep only letters
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# --- Load model and vectorizer ---
def reload_model_and_vectorizer():
    global model, vectorizer
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print("✅ Model and vectorizer loaded")
        reload_dataset_vectors()  # reload dataset vectors after model reload
    except Exception as e:
        print(f"⚠️ Error loading model/vectorizer: {e}")
        model, vectorizer = None, None

# --- Prediction Function ---
def predict_news(title, text):
    if model is None or vectorizer is None:
        return 'unknown', 0.0

    combined_text = f"{title} {text}"
    preprocessed_text = preprocess_text(combined_text)

    if not preprocessed_text.strip():
        return 'unknown', 0.0

    text_vectorized = vectorizer.transform([preprocessed_text])
    prediction_proba = model.predict_proba(text_vectorized)[0]
    prediction_label = model.predict(text_vectorized)[0]

    label_map = {1: 'True', 0: 'Fake'}
    return label_map[prediction_label], float(max(prediction_proba))

# --- Extract text from URL ---
def extract_article_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return text if text else None
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return None

# --- Append news to CSV ---
def append_news_to_csv(title, text, label):
    filename = "True.csv" if label == "True" else "Fake.csv"
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow([title, text])

# --- Retrain Model ---
def retrain_model():
    global model, vectorizer
    try:
        true_path = os.path.join(DATA_DIR, 'True.csv')
        fake_path = os.path.join(DATA_DIR, 'Fake.csv')

        df_true = pd.read_csv(true_path, names=['title','text'], encoding='utf-8', on_bad_lines='skip')
        df_fake = pd.read_csv(fake_path, names=['title','text'], encoding='utf-8', on_bad_lines='skip')

        df_true['label'] = 1
        df_fake['label'] = 0
        df = pd.concat([df_true, df_fake], ignore_index=True)
        df['combined'] = (df['title'].fillna('') + ' ' + df['text'].fillna('')).apply(preprocess_text)

        X = df['combined']
        y = df['label']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        vectorizer_new = TfidfVectorizer(stop_words='english', max_df=0.7)
        X_train_vec = vectorizer_new.fit_transform(X_train)
        X_test_vec = vectorizer_new.transform(X_test)

        model_new = LogisticRegression(max_iter=1000)
        model_new.fit(X_train_vec, y_train)

        # Evaluate
        y_pred = model_new.predict(X_test_vec)
        print("📊 Model Evaluation:")
        print(classification_report(y_test, y_pred, target_names=['Fake', 'True']))

        # Save
        model, vectorizer = model_new, vectorizer_new
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)

        print("✅ Retraining complete & model saved")
        reload_dataset_vectors()

    except Exception as e:
        print(f"❌ Retrain error: {e}")
        traceback.print_exc()

# --- Precompute dataset vectors ---
def reload_dataset_vectors():
    global dataset_df, dataset_vectors
    if model is None or vectorizer is None:
        return
    df_real = pd.read_csv(os.path.join(DATA_DIR, 'True.csv'), names=['title','text'], on_bad_lines='skip')
    df_fake = pd.read_csv(os.path.join(DATA_DIR, 'Fake.csv'), names=['title','text'], on_bad_lines='skip')
    df_real['label'] = 'True'
    df_fake['label'] = 'Fake'
    dataset_df = pd.concat([df_real, df_fake], ignore_index=True)
    dataset_df['combined'] = (dataset_df['title'].fillna('') + ' ' + dataset_df['text'].fillna('')).apply(preprocess_text)
    dataset_vectors = vectorizer.transform(dataset_df['combined'])

# --- Trusted Domains ---
trusted_domains = [
    "bbc.com","cnn.com","reuters.com","nytimes.com","theguardian.com",
    "washingtonpost.com","aljazeera.com","npr.org","apnews.com","forbes.com"
]

# Initial load
reload_model_and_vectorizer()
