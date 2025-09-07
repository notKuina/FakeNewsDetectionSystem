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

# Import ML utilities
from .model.ml_utils import (
    preprocess_text as clean_text,
    extract_article_text_from_url,
    append_news_to_csv,
    retrain_model,
    reload_model_and_vectorizer,
    trusted_domains,
    model,
    vectorizer,
    DATA_DIR,
)


logger = logging.getLogger(__name__)
reload_model_and_vectorizer()


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
            result = "True" if pred == 1 else "Fake"
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

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print(" Model and Vectorizer loaded successfully")
except Exception as e:
    model = None
    vectorizer = None
    print(f" Error loading model/vectorizer: {e}")


# ---------------------- UNIFIED ANALYZE ----------------------
MAX_INPUT_LENGTH = 5000

@csrf_exempt
@require_http_methods(["POST"]) 
def analyze(request):

    try:
        data = json.loads(request.body)
        user_input = data.get('user_input', '').strip()
        method = data.get('method', '').strip()

        if not user_input or not method:
            return JsonResponse({'error': 'Missing input or method.'}, status=400)

        # -------------------- 1. Direct Input --------------------
        if method == 'input':
            vect = vectorizer.transform([clean_text(user_input)])
            pred = model.predict(vect)[0]
            proba = model.predict_proba(vect)[0]
            return JsonResponse({
                "result": "True" if pred == 1 else "Fake",
                "confidence": round(max(proba) * 100, 2),
                "article_text": user_input
            })

        # -------------------- 2. Dataset Check --------------------
        elif method == 'dataset':
            df_real = pd.read_csv(os.path.join(DATA_DIR, 'True.csv'), on_bad_lines='skip')
            df_fake = pd.read_csv(os.path.join(DATA_DIR, 'Fake.csv'), on_bad_lines='skip')

            df_real['label'] = 'True'
            df_fake['label'] = 'Fake'
            df = pd.concat([df_real[['title','text','label']], df_fake[['title','text','label']]], ignore_index=True)

            df['combined'] = (df['title'].fillna('') + ' ' + df['text'].fillna('')).apply(clean_text)

            cleaned_input = clean_text(user_input)
            dataset_vectors = vectorizer.transform(df['combined'])
            user_vector = vectorizer.transform([cleaned_input])

            similarity_scores = cosine_similarity(user_vector, dataset_vectors)[0]

            top_indices = similarity_scores.argsort()[::-1]
            
            top_matches = []
            for idx in top_indices[:5]:
                if similarity_scores[idx] < 0.01:  # lower threshold to catch more matches
                    continue

                article_text = df.iloc[idx]['text'] or ''
                article_vector = vectorizer.transform([clean_text(article_text)])
                pred = model.predict(article_vector)[0]
                predicted_label = 'True' if pred == 1 else 'Fake'
                actual_label = df.iloc[idx]['label']  # from CSV

                top_matches.append({
                    'title': df.iloc[idx]['title'] or 'No Title',
                    'text': article_text[:300],
                    'predicted': predicted_label,
                    'actual': actual_label,
                    'similarity': round(float(similarity_scores[idx]), 3),
                    'correct': predicted_label == actual_label
                })


            if top_matches:
                real_votes = sum(1 for a in top_matches if a['actual'] == 'True')
                fake_votes = sum(1 for a in top_matches if a['actual'] == 'Fake')

                if real_votes > fake_votes:
                    final_pred = 'True'
                elif fake_votes > real_votes:
                    final_pred = 'Fake'
                else:
                    pred = model.predict(user_vector)[0]
                    final_pred = "True" if pred == 1 else "Fake"

                return JsonResponse({
                    "result": f"{final_pred} (based on similar articles)",
                    "article_text": user_input,
                    "articles": top_matches,
                    "found_matches": True
                })
            else:
                pred = model.predict(user_vector)[0]
                prediction = "True" if pred == 1 else "Fake"
                return JsonResponse({
                    "result": prediction,
                    "article_text": user_input,
                    "articles": [],
                    "found_matches": False
                })

        # -------------------- 3. URL Check --------------------
       
        elif method == 'url':
            domain = urlparse(user_input).netloc.lower()
            article_text = extract_article_text_from_url(user_input)

            if any(trusted in domain for trusted in trusted_domains):
                return JsonResponse({
                    "result": "True (Trusted Source)",
                    "article_text": article_text or "No article content found."
                })
            elif article_text and model and vectorizer:
                cleaned_article = clean_text(article_text)
                vect = vectorizer.transform([cleaned_article])
                pred = model.predict(vect)[0]
                result = "True" if pred == 1 else "Fake"
                return JsonResponse({
                    "result": result,
                    "article_text": article_text
                })
            else:
                return JsonResponse({
                    "result": "Unable to analyze this URL",
                    "article_text": "No article content found."
                })

        else:
            return JsonResponse({'error': 'Invalid method. Use "input", "dataset" or "url"'}, status=400)

    except Exception as e:
        print(f"[ERROR] analyze failed: {e}")
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
