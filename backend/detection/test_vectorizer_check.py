import os
import json
import pandas as pd
import joblib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'detection', 'model', 'lr_model.jb')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'detection', 'model', 'vectorizer.jb')
TRUE_PATH = os.path.join(BASE_DIR, 'detection', 'data', 'True.csv')
FAKE_PATH = os.path.join(BASE_DIR, 'detection', 'data', 'Fake.csv')

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
