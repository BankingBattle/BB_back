from datetime import datetime
from datetime import timedelta
from django.db import models
from bb_back.core.models.user import User


class Game(models.Model):
    Name = models.CharField(max_length=30)
    # Organizater = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now())
    players = models.ManyToManyField(User)
    finish_at = models.DateTimeField(default=datetime.now() + timedelta(days=1))
    is_active = models.BooleanField(default=True)
