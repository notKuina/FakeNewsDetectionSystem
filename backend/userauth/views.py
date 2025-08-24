import json
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password

logger = logging.getLogger(__name__)

# Render home page
def home(request):
    return render(request, 'home.html') 

# Render Login Page and process classic form POST login
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('psw', '')

        if not email or not password:
            return render(request, 'userauth/Login.html', {'error': 'Email and password are required.'})

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return render(request, 'userauth/Login.html', {'error': 'Invalid email or password.'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('adminpanel:admin_dashboard') 
            return redirect('userauth:user_page') 
        else:
            return render(request, 'userauth/Login.html', {'error': 'Invalid email or password.'})
    else:
        return render(request, 'userauth/Login.html')


# Handle login POST requests via JSON API
@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
    except Exception:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    if not email or not password:
        return JsonResponse({"error": "Email and password required."}, status=400)

    try:
        user_obj = User.objects.get(email=email)
        username = user_obj.username
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        redirect_url = "/detection/adminDashboard/" if (user.is_staff or user.is_superuser) else "/userPage/"
        return JsonResponse({"message": "Login successful", "redirect": redirect_url})
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=401)


# Render Registration page and process classic form POST registration
def register_view(request):
    if request.method == 'POST':
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not fname or not lname or not email or not password:
            return render(request, 'userauth/Registration.html', {'error': 'All fields are required.'})

        if User.objects.filter(username=email).exists():
            return render(request, 'userauth/Registration.html', {'error': 'User with this email already exists.'})

        user = User.objects.create(
            username=email,
            first_name=fname,
            last_name=lname,
            email=email,
            password=make_password(password),
        )
        user.save()
        return redirect('userauth:login')  # Add namespace if your login url is namespaced

    else:
        return render(request, 'userauth/Registration.html')


# Handle user registration POST via JSON API
@csrf_exempt 
def register_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            fname = data.get('fname', '').strip()
            lname = data.get('lname', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')

            if not fname or not lname or not email or not password:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            if User.objects.filter(username=email).exists():
                return JsonResponse({'error': 'User with this email already exists.'}, status=400)

            user = User.objects.create(
                username=email,
                first_name=fname,
                last_name=lname,
                email=email,
                password=make_password(password),
            )
            user.save()
            logger.info(f"User created with id: {user.id}, username: {user.username}")
            return JsonResponse({'message': 'User registered successfully!'})
        except Exception as e:
            logger.error(f"Exception in register_user: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


def user_page(request):
    if not request.user.is_authenticated:
        return redirect('userauth:login') 

    return render(request, 'detection/userPage.html', {
        'first_name': request.user.first_name or request.user.username
    })


def logout_view(request):
    logout(request)
    return redirect('detection:home')




def forgot_password(request):
    if request.method == 'POST':
        # TODO: handle email input, send reset link or code
        email = request.POST.get('email')
        # You can add logic here to check email & send email
        # For now, just render success or same page
        context = {'message': 'If the account exists, a reset email has been sent.'}
        return render(request, 'userauth/forgot_password.html', context)

    return render(request, 'userauth/ForgotPassword.html')
