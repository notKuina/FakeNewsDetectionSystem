from django.shortcuts import render, get_object_or_404, redirect
from detection.models import SubmittedNews
from detection.model.ml_utils import retrain_model
from detection.model.lr_model import reload_model
import json
import os
import csv
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods,require_POST
from django.db import transaction
from django.conf import settings
import pandas as pd
from django.contrib.auth import logout
from adminpanel import views

# Decorator to allow only staff/admin users
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

def append_news_to_csv(title, text, label):
    DATA_DIR = os.path.join(settings.BASE_DIR, 'detection', 'data')
    csv_file = os.path.join(DATA_DIR, f"{label}.csv")

    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=['title', 'text'])
    else:
        df = pd.read_csv(csv_file, delimiter=',', quotechar='"', on_bad_lines='skip')

    new_row = {'title': title, 'text': text}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_file, index=False, quoting=csv.QUOTE_ALL)


@admin_required
def admin_dashboard(request):
    users = User.objects.all()
    submitted_news_titles = SubmittedNews.objects.values_list('title', flat=True).order_by('-submitted_at')
    return render(request, 'detection/adminDashboard.html', {
        'users': users,
        'submitted_news_titles': submitted_news_titles,
    })

@admin_required
def get_all_users(request):
    users = User.objects.all().values('id', 'username', 'email', 'first_name', 'last_name')
    data = []
    for user in users:
        contributions = SubmittedNews.objects.filter(user_id=user['id']).values(
            'id', 'title', 'content', 'is_approved', 'submitted_at'
        )
        data.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'fname': user['first_name'],
            'lname': user['last_name'],
            'contributions': list(contributions),
        })
    return JsonResponse(data, safe=False)


@admin_required
@require_http_methods(['DELETE'])
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Prevent self-deletion
    if user == request.user:
        return JsonResponse({'error': 'You cannot delete yourself.'}, status=400)
    user.delete()
    return JsonResponse({'message': 'User deleted successfully.'})

@admin_required
@require_http_methods(['DELETE'])
def delete_contribution(request, contrib_id):
    contribution = get_object_or_404(SubmittedNews, id=contrib_id)
    contribution.delete()
    return JsonResponse({'message': 'Contribution deleted successfully.'})
@admin_required
@require_http_methods(['PUT'])
def update_contribution(request, contrib_id):
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()

        if not title or not content:
            return JsonResponse({'error': 'Title and content are required'}, status=400)

        contribution = SubmittedNews.objects.get(id=contrib_id)
        contribution.title = title
        contribution.content = content
        contribution.save()

        return JsonResponse({'message': 'Contribution updated successfully'})

    except SubmittedNews.DoesNotExist:
        return JsonResponse({'error': 'Contribution not found or unauthorized'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_required
@require_http_methods(['POST'])
def approve_contribution(request, contrib_id, csv_type):
    if csv_type not in ['True', 'Fake']:
        return JsonResponse({'error': 'Invalid csv_type.'}, status=400)

    with transaction.atomic():
        contribution = get_object_or_404(SubmittedNews, id=contrib_id)
        contribution.is_approved = True
        contribution.save()

        # Append news to the CSV file
        append_news_to_csv(title=contribution.title, text=contribution.content, label=csv_type)
       
        retrain_model() 
        reload_model()

    return JsonResponse({'message': f'Contribution approved and added to {csv_type}.csv'})

@require_POST
def admin_logout_view(request):
    logout(request)
    return redirect('userauth:login')  
