from django.shortcuts import redirect
from django.urls import path, include,reverse
from django.contrib import admin
# from adminpanel import views as admin_views 

def redirect_login(request):
    return redirect(reverse('userauth:login'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('detection.urls', 'detection'), namespace='detection')),
    path('userauth/', include(('userauth.urls', 'userauth'), namespace='userauth')),  # <--- note the tuple and namespace
    path('login/', redirect_login),  # Redirect /login/ to /userauth/login/
    path('adminpanel/', include('adminpanel.urls')),
]
