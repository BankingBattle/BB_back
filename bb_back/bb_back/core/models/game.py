from django.db import models


class Game(models.Model):
    name = models.CharField(null=False, max_length=63)
    description = models.TextField(null=True)
    logo = models.FileField(upload_to="submits", null=True)

    datetime_start = models.DateTimeField(null=True)
    datetime_end = models.DateTimeField(null=True)

    is_active = models.BooleanField(default=True)
