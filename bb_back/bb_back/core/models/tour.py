from datetime import datetime
from datetime import timedelta
from django.db import models
from bb_back.core.models.game import Game


class Tour(models.Model):
    # Organizater = models.ForeignKey(User, on_delete=models.CASCADE)
    Game = models.ForeignKey(Game)
    Number = models.IntegerField(default=0)
    NumberOfScores = models.IntegerField(default=0)
    finish_at = models.DateTimeField(default=datetime.now() + timedelta(days=1))
