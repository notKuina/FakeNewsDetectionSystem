import os
import csv
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, 'detection', 'model', 'lr_model.jb')
VECTORIZER_PATH = os.path.join(settings.BASE_DIR, 'detection', 'model', 'vectorizer.jb')
DATA_DIR = os.path.join(settings.BASE_DIR, 'detection', 'data')

model = None
vectorizer = None

def reload_model():
    global model, vectorizer
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print("Model and vectorizer reloaded into memory.")
    except Exception as e:
        print(f"Error loading model/vectorizer: {e}")
        model = None
        vectorizer = None

def append_news_to_csv(title, text, label):
    path = os.path.join(DATA_DIR, f"{label}.csv")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow([title, text])

def retrain_model():
    global model, vectorizer
    try:
        true_path = os.path.join(DATA_DIR, 'True.csv')
        fake_path = os.path.join(DATA_DIR, 'Fake.csv')

        df_true = pd.read_csv(true_path, names=['title', 'text'], on_bad_lines='skip') if os.path.exists(true_path) else pd.DataFrame(columns=['title', 'text'])
        df_fake = pd.read_csv(fake_path, names=['title', 'text'], on_bad_lines='skip') if os.path.exists(fake_path) else pd.DataFrame(columns=['title', 'text'])

        df_true['label'] = 1
        df_fake['label'] = 0

        df = pd.concat([df_true, df_fake], ignore_index=True)
        df['combined'] = df['title'].fillna('') + ' ' + df['text'].fillna('')

        X = df['combined']
        y = df['label']

        vectorizer = TfidfVectorizer(max_features=10000)
        X_vect = vectorizer.fit_transform(X)

        model = LogisticRegression(max_iter=1000)
        model.fit(X_vect, y)

        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)
        print("Model retrained and saved.")

        globals()['model'] = model
        globals()['vectorizer'] = vectorizer
    except Exception as e:
        print(f"Error during retraining: {e}")

# Only reload model on server start — do NOT retrain automatically here
reload_model()
