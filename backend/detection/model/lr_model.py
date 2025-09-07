# detection/model/lr_model.py
import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from.ml_utils import preprocess_text
from django.conf import settings
from .ml_utils import reload_model_and_vectorizer as reload_model


DATA_DIR = os.path.join(settings.BASE_DIR, "detection", "data")
MODEL_PATH = os.path.join(settings.BASE_DIR, "detection", "model", "lr_model.jb")
VECTORIZER_PATH = os.path.join(settings.BASE_DIR, "detection", "model", "vectorizer.jb")

def train_from_scratch():
    true_path = os.path.join(DATA_DIR, "True.csv")
    fake_path = os.path.join(DATA_DIR, "Fake.csv")

    df_true = pd.read_csv(true_path)
    df_fake = pd.read_csv(fake_path)

    df_true["class"] = 1
    df_fake["class"] = 0

    df = pd.concat([df_true, df_fake], ignore_index=True)
    df["combined"] = (df["title"].fillna("") + " " + df["text"].fillna("")).apply(preprocess_text)

    X = df["combined"]
    y = df["class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(stop_words="english", max_df=0.7)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    print("Evaluation Report:\n", classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"Model saved to {MODEL_PATH}, Vectorizer saved to {VECTORIZER_PATH}")

if __name__ == "__main__":
    train_from_scratch()
