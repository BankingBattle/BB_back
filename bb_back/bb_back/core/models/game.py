from django.db import models


class Game(models.Model):
    name = models.CharField(null=False, max_length=63)
    description = models.TextField(null=True)

    is_active = models.BooleanField(default=True)
