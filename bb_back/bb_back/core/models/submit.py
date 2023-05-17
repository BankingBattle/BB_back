from django.db import models
from django.utils import timezone


class Submit(models.Model):
    file = models.FileField(upload_to="submits", null=True)
    id_command = models.IntegerField(null=True)
    round_num = models.IntegerField(null=True)
    final = models.BooleanField(null=False, default=False)
    score = models.FloatField(null=False, default=0)
    created_at = models.DateTimeField(default=timezone.now)
