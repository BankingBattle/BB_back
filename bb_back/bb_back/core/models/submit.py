from django.db import models


class Submit(models.Model):
    file = models.FileField(upload_to="submits", null=True)
    id_command = models.IntegerField(null=True)
    round_num = models.IntegerField(null=True)
