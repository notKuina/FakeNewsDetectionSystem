import os
import json
import logging
import pandas as pd
import joblib
import re
import string
import traceback
from urllib.parse import urlparse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import SubmittedNews
from sklearn.metrics.pairwise import cosine_similarity

from difflib import get_close_matches
import numpy as np
from .model.ml_utils import preprocess_text as clean_text

from .model.ml_utils import (
    extract_article_text_from_url,
    append_news_to_csv,
    retrain_model,vectorizer,model,
    reload_model_and_vectorizer,
    trusted_domains,
    MODEL_PATH,
    VECTORIZER_PATH,
    DATA_DIR,
)

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'detection/home.html')

@login_required
def my_submissions(request):
    news_list = SubmittedNews.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'detection/my_submissions.html', {'news_list': news_list})

def review_news(request):
    news_list = SubmittedNews.objects.all()
    return render(request, 'review_news.html', {'news_list': news_list})

# ---------------------- CHECK / SUBMIT NEWS ----------------------

@csrf_exempt
@require_http_methods(["POST"])
def check_news(request):
    try:
        data = json.loads(request.body)
        user_input = data.get("text", "").strip()
        if not user_input:
            return JsonResponse({"error": "Text input is required."}, status=400)

        if model and vectorizer:
            cleaned_input = clean_text(user_input)  
            vect = vectorizer.transform([cleaned_input])
            pred = model.predict(vect)[0]
            result = "Real" if pred == 1 else "Fake"
            return JsonResponse({"result": result})
        else:
            return JsonResponse({"error": "Model or vectorizer not loaded."}, status=500)
    except Exception:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def submit_news(request):
    try:
        data = json.loads(request.body)
        news_text = data.get("text") or data.get("content") or ""
        user_title = data.get("title", "").strip()

        if not news_text.strip():
            return JsonResponse({"error": "No text provided."}, status=400)

        def generate_title(text):
            return text.split('.')[0].strip()[:100] if '.' in text else text.strip()[:100]

        title = user_title or generate_title(news_text)

        SubmittedNews.objects.create(user=request.user, title=title, content=news_text)

        return JsonResponse({"message": "News received!", "title": title, "content": news_text})

    except Exception:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

# ---------------------- ANALYZE (Guest) ----------------------

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'detection', 'model', 'lr_model.jb')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'detection', 'model', 'vectorizer.jb')

# Load model & vectorizer once
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# ---------------------- ANALYZE (Guest input) ----------------------
@csrf_exempt
@require_http_methods(["POST"])
def analyze(request):
    try:
        data = json.loads(request.body)
        user_input = data.get('user_input', '').strip()

        if not user_input:
            return JsonResponse({'error': 'No input text provided.'}, status=400)

        # Vectorize and predict
        transformed_input = vectorizer.transform([user_input])
        prediction = model.predict(transformed_input)[0]  # 0 = Fake, 1 = Real
        probability = model.predict_proba(transformed_input)[0]

        return JsonResponse({
            'input_text': user_input,
            'prediction': 'Real' if prediction == 1 else 'Fake',
            'confidence': round(max(probability) * 100, 2)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ---------------------- CHECK FROM DATASETS ----------------------
@csrf_exempt
@require_http_methods(["GET"])
def check_datasets(request):
    try:
        # Load datasets
        true_df = pd.read_csv(TRUE_PATH)
        fake_df = pd.read_csv(FAKE_PATH)

        # Add labels: 1 = Real, 0 = Fake
        true_df['label'] = 1
        fake_df['label'] = 0

        # Combine
        df = pd.concat([true_df, fake_df], ignore_index=True)

        # Predict with model to ensure ML-based validation
        texts = df['text'].astype(str).tolist()
        transformed = vectorizer.transform(texts)
        predictions = model.predict(transformed)

        df['model_prediction'] = ['Real' if p == 1 else 'Fake' for p in predictions]

        # Convert to JSON
        records = df[['title', 'text', 'model_prediction']].to_dict(orient='records')

        return JsonResponse({'data': records})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@csrf_exempt
@require_http_methods(["POST"])
def analyze(request):
    try:
        data = json.loads(request.body)
        user_input = data.get('user_input', '').strip()
        method = data.get('method', '').strip()

        if not user_input or not method:
            return JsonResponse({'error': 'Missing input or method.'}, status=400)

        if method == 'url':
            domain = urlparse(user_input).netloc.lower()
            article_text = extract_article_text_from_url(user_input)

            if any(trusted in domain for trusted in trusted_domains):
                return JsonResponse({
                    "result": "Real (Trusted Source)",
                    "article_text": article_text or "No article content found."
                })
            elif article_text and model and vectorizer:
                cleaned_article = clean_text(article_text)
                vect = vectorizer.transform([cleaned_article])
                pred = model.predict(vect)[0]
                result = "Real" if pred == 1 else "Fake"
                return JsonResponse({
                    "result": result,
                    "article_text": article_text
                })
            else:
                return JsonResponse({
                    "result": "Unable to analyze this URL",
                    "article_text": "No article content found."
                })

        elif method == 'dataset':
            try:
                # Load datasets
                df_real = pd.read_csv(os.path.join(DATA_DIR, 'True.csv'), on_bad_lines='skip')
                df_fake = pd.read_csv(os.path.join(DATA_DIR, 'Fake.csv'), on_bad_lines='skip')

                df_real = df_real[['title', 'text']]
                df_fake = df_fake[['title', 'text']]

                df_real['label'] = 'Real'
                df_fake['label'] = 'Fake'
                df = pd.concat([df_real, df_fake], ignore_index=True)
                print(f"Loaded {len(df)} articles from dataset")

                df['combined'] = (df['title'].fillna('') + ' ' + df['text'].fillna('')).apply(clean_text)

                # Debug: vectorizer vocab size
                print("Vectorizer vocabulary size:", len(vectorizer.vocabulary_))

                cleaned_input = clean_text(user_input)
                print("Cleaned user input:", cleaned_input)

                dataset_vectors = vectorizer.transform(df['combined'])
                user_vector = vectorizer.transform([cleaned_input])

                # Debug: user vector non-zero entries
                print("User vector non-zero entries:", user_vector.nnz)

                similarity_scores = cosine_similarity(user_vector, dataset_vectors)[0]
                print("Max similarity score:", similarity_scores.max())

                # Select top 5 similar articles above threshold 0.05
                top_indices = similarity_scores.argsort()[::-1]
                threshold = 0.05
                top_matches = []

                for idx in top_indices:
                    score = similarity_scores[idx]
                    if score < threshold:
                        break
                    top_matches.append({
                        'title': df.iloc[idx]['title'] or 'No Title',
                        'text': (df.iloc[idx]['text'] or '')[:300],
                        'label': df.iloc[idx]['label'],
                        'similarity': round(float(score), 3)
                    })
                    if len(top_matches) >= 5:
                        break

                print(f"Found {len(top_matches)} similar articles")

                if top_matches:
                    # Count votes by label
                    real_votes = sum(1 for a in top_matches if a['label'] == 'Real')
                    fake_votes = sum(1 for a in top_matches if a['label'] == 'Fake')

                    # Majority vote or tie breaker
                    if real_votes > fake_votes:
                        final_pred = 'Real'
                    elif fake_votes > real_votes:
                        final_pred = 'Fake'
                    else:
                        # Tie: fallback to ML model
                        user_vec = vectorizer.transform([cleaned_input])
                        pred = model.predict(user_vec)[0]
                        final_pred = "Real" if pred == 1 else "Fake"

                    return JsonResponse({
                        "result": f"{final_pred} (based on similar articles)",
                        "article_text": user_input,
                        "articles": top_matches,
                        "found_matches": True
                    })
                else:
                    # No good matches, fallback to ML model
                    if model and vectorizer:
                        user_vec = vectorizer.transform([cleaned_input])
                        pred = model.predict(user_vec)[0]
                        prediction = "Real" if pred == 1 else "Fake"
                        return JsonResponse({
                            "result": prediction,
                            "article_text": user_input,
                            "articles": [],
                            "found_matches": False
                        })
                    else:
                        return JsonResponse({
                            "result": "Unable to analyze - model not available",
                            "article_text": user_input,
                            "articles": [],
                            "found_matches": False
                        })

            except Exception as dataset_error:
                print(f"Dataset error: {dataset_error}")
                traceback.print_exc()
                return JsonResponse({
                    "result": "Error loading dataset",
                    "article_text": user_input,
                    "error": str(dataset_error)
                })

        else:
            return JsonResponse({'error': 'Invalid method. Use "url" or "dataset"'}, status=400)

    except Exception as e:
        print("Exception in analyze view:", e)
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


# ---------------------- USER CONTRIBUTIONS ----------------------

@login_required
def get_contributions(request):
    contributions = SubmittedNews.objects.filter(user=request.user).order_by('-created_at')
    data = [{
        "id": c.id,
        "title": c.title,
        "content": c.content,
        "is_approved": c.is_approved,
        "created_at": c.created_at.isoformat(),
    } for c in contributions]
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def edit_contribution(request, id):
    try:
        data = json.loads(request.body)
        title = data.get("title", "").strip()
        content = data.get("content", "").strip()

        if not title or not content:
            return JsonResponse({"error": "Title and content required."}, status=400)

        contribution = SubmittedNews.objects.get(id=id, user=request.user)
        contribution.title = title
        contribution.content = content
        contribution.save()

        return JsonResponse({"message": "Contribution updated successfully!"})

    except SubmittedNews.DoesNotExist:
        return JsonResponse({"error": "Contribution not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_contribution(request, id):
    try:
        contribution = SubmittedNews.objects.get(id=id, user=request.user)
        contribution.delete()
        return JsonResponse({"message": "Contribution deleted successfully."})
    except SubmittedNews.DoesNotExist:
        return JsonResponse({"error": "Contribution not found or unauthorized."}, status=404)

# ---------------------- ADMIN APPROVAL ----------------------

@csrf_exempt
@login_required  # Optional: restrict to staff only using @staff_member_required
def update_status(request, news_id, action):
    news_item = get_object_or_404(SubmittedNews, id=news_id)

    if action == "approve":
        news_item.is_approved = True
        label = 'True'
    elif action == "disapprove":
        news_item.is_approved = False
        label = 'Fake'
    else:
        return redirect('review_news')

    news_item.save()
    append_news_to_csv(title=news_item.title, text=news_item.content, label=label)
    retrain_model()
    reload_model_and_vectorizer()
    return redirect('review_news')
