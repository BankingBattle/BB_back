from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .user import User
from .game import Game


class Team(models.Model):
    name = models.CharField(max_length=15)
    description = models.TextField(max_length=255, blank=True, null=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    members = models.ManyToManyField(User, related_name='teams')

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='teams')

    class Meta:
        unique_together = [['name', 'game']]

    def validate_unique_teams(self):
        if not self.id:
            return

        if len(set(self.members.all())) != len(self.members.all()):
            raise ValidationError(_('A user cannot be added to the same team more than once.'))

        for member in self.members.all():
            if self.game.teams.filter(members=member).exclude(id=self.id).exists():
                raise ValidationError(_("User is already a member of another team for this game."))

    def clean(self):
        self.validate_unique_teams()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
