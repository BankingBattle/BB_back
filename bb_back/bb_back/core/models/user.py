from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=63)
    login = models.CharField(max_length=30)
    hashed_pass = models.CharField(max_length=255)
