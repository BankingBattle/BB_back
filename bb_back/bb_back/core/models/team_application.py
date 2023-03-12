from django.db import models

from .team import Team
from .user import User


class TeamApplication(models.Model):
    STATUS_CHOICES = [
        ('Accepted', 'Accepted'),
        ('Pending', 'Pending'),
        ('Declined', 'Declined'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES,
                              default='Pending',
                              max_length=20)
