from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass


class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="search_history", null=True, blank=True)
    symbol = models.CharField(max_length=10, default="UNKNOWN")
    days = models.PositiveIntegerField(default=30)
    search_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} searched for {self.symbol} ({self.days} days) on {self.search_date}"