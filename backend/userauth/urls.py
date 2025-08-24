from django.urls import path
from.import views

app_name = 'userauth'

urlpatterns=[
    path('', views.home, name='home'),  
    path('login/', views.login_view,name='login'),
    path('login', views.login_view),
    path('login_user/', views.login_user, name='login_user'),  
    path('register/', views.register_view, name='register'), 
    path('register_user/', views.register_user, name='register_user'),
    path('userpage/', views.user_page, name='user_page'),  
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password')
]