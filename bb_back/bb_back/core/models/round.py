from django.db import models

from .game import Game


class Round(models.Model):
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=63)
    description = models.TextField(null=True)

    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    data_of_round = models.FileField(upload_to="round_data", null=True)
    round_target = models.FileField(upload_to="round_target", null=True)
