from django.contrib import admin
from detection.models import SubmittedNews

@admin.register(SubmittedNews)
class SubmittedNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('title', 'content', 'user__username')
