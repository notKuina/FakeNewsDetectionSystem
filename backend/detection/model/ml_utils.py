import csv
import os
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

trusted_domains = [
    "bbc.com", "cnn.com", "reuters.com", "nytimes.com",
    "theguardian.com", "npr.org", "forbes.com", "bloomberg.com","kantipur.com","thehimalayantimes.com"
]

# --- Global Variables for Loaded Model ---
model = None
vectorizer = None

# --- Preprocessing Function ---
def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove non-letters
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
        print("Model and vectorizer loaded successfully!")
    except FileNotFoundError:
        print(f"Model or vectorizer file not found. Expected at {MODEL_PATH} and {VECTORIZER_PATH}")
        model, vectorizer = None, None
    except Exception as e:
        print(f"Error loading model/vectorizer: {e}")
        model, vectorizer = None, None

reload_model_and_vectorizer()

# --- Prediction Function ---
def predict_news(title, text):
    if model is None or vectorizer is None:
        return 'unknown', 0.0

    combined_text = f"{title} {text}"
    preprocessed_text = preprocess_text(combined_text)

    if not preprocessed_text:
        return 'unknown', 0.0

    text_vectorized = vectorizer.transform([preprocessed_text])
    prediction_proba = model.predict_proba(text_vectorized)[0]
    prediction_label_int = model.predict(text_vectorized)[0]

    label_map = {1: 'Real', 0: 'Fake'}
    ml_result = label_map.get(prediction_label_int, 'unknown')
    ml_confidence = max(prediction_proba)

    return ml_result, float(ml_confidence)

# --- Extract text from URL ---
def extract_article_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        return text if text else None
    except Exception as e:
        print(f"Error extracting article text from URL: {e}")
        return None

# --- Append news to CSV ---
def append_news_to_csv(title, text, label):
    filename = "True.csv" if label in ["True", 1] else "Fake.csv"
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow([title, text])


def retrain_model():
    global model, vectorizer
    try:
        true_path = os.path.join(DATA_DIR, 'True.csv')
        fake_path = os.path.join(DATA_DIR, 'Fake.csv')

        print(f"Checking existence: True.csv -> {os.path.exists(true_path)}, Fake.csv -> {os.path.exists(fake_path)}")

        df_true = pd.read_csv(true_path, quotechar='"', on_bad_lines='skip', encoding='utf-8-sig')
        df_fake = pd.read_csv(fake_path, quotechar='"', on_bad_lines='skip', encoding='utf-8-sig')

        # Drop unwanted columns
        for df in [df_true, df_fake]:
            for col in ['subject', 'date']:
                if col in df.columns:
                    df.drop(columns=[col], inplace=True)

        df_true = df_true[['title', 'text']]
        df_fake = df_fake[['title', 'text']]

        print(f"Loaded datasets: True articles = {len(df_true)}, Fake articles = {len(df_fake)}")

        df_true['label'] = 1
        df_fake['label'] = 0

        df = pd.concat([df_true, df_fake], ignore_index=True)
        df.dropna(subset=['text'], inplace=True)

        # Combine title + text, preprocess
        df['combined'] = (df['title'].fillna('') + ' ' + df['text'].fillna('')).apply(preprocess_text)

        X = df['combined']
        y = df['label']

        # Split 50/50 train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.5, random_state=42, stratify=y
        )

        vectorizer_new = TfidfVectorizer(stop_words='english', max_df=0.7)
        X_train_vec = vectorizer_new.fit_transform(X_train)
        X_test_vec = vectorizer_new.transform(X_test)

        model_new = LogisticRegression(max_iter=1000)
        model_new.fit(X_train_vec, y_train)

        # Evaluate on test set and print report
        y_pred = model_new.predict(X_test_vec)
        print("Model evaluation on test set:")
        print(classification_report(y_test, y_pred, target_names=['Fake', 'Real']))

        # Update globals and save
        vectorizer = vectorizer_new
        model = model_new

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)

        print("Retraining complete and model saved.")

    except Exception as e:
        print(f"Error retraining model: {e}")
        traceback.print_exc()
