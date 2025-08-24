from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class News(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='detection_news')
    title = models.CharField(max_length=255)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_fake = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.title

    def is_approved(self):
        return self.status == 'approved'

    class Meta:
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['submitted_at']),
        ]


class Contribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='detection_contributions')
    title = models.CharField(max_length=255)   
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contribution by {self.user.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


class SubmittedNews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='detection_submittednews')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  # editable or last updated time
    submitted_at = models.DateTimeField(auto_now_add=True)   # first submission time

    def status(self):
        return "Approved" if self.is_approved else "Pending"

    def __str__(self):
        # Show title if exists, fallback to excerpt + username
        return self.title if self.title else f"{self.content[:30]}... by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
