from django.db import models


class Submit(models.Model):
    file = models.FileField(upload_to="submits", null=True)
    id_command = models.IntegerField(null=True)
    round_num = models.IntegerField(null=True)
    final = models.BooleanField(null=False, default=False)
    score = models.IntegerField(null=False)
    create_at = models.DateTimeField()