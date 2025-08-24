from django.urls import path,include
from . import views
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

app_name='detection'

urlpatterns = [
    # User URLs
    path('', views.home, name='home'),
    path('check/', views.check_news, name='check_news'),
    path('analyze/', views.analyze, name='analyze'),
    path('submit/', views.submit_news, name='submit_news'),
    path('my_submissions/', views.my_submissions, name='my_submissions'),
    path('get_contributions', views.get_contributions, name='get_contributions'),
    path('edit/<int:id>/', views.edit_contribution, name='edit_contribution'),
    path('delete/<int:id>/', views.delete_contribution, name='delete_contribution'),


]
