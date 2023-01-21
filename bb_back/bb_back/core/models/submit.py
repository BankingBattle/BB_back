from django.db import models

# Создайте модели здесь.


class Submit(models.Model):
    file = models.FileField(upload_to="submit", null=True)
    id_command = models.IntegerField(null=True)
