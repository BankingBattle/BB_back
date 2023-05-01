from django.db import models
from datetime import datetime


class Submit(models.Model):
    file = models.FileField(upload_to="submits", null=True)
    id_command = models.IntegerField(null=True)
    round_num = models.IntegerField(null=True)
    final = models.BooleanField(null=False, default=False)
    score = models.FloatField(null=False, default=0)
    create_at = models.DateTimeField(default=datetime.min)
