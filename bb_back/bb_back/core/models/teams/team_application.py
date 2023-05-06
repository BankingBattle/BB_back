from django.db import models
from bb_back.core.constants import TeamApplicationStatusesEnum


class TeamApplication(models.Model):
    game = models.ForeignKey("Game", on_delete=models.DO_NOTHING, null=True)
    team_name = models.CharField(max_length=63)
    status = models.PositiveSmallIntegerField(
        default=TeamApplicationStatusesEnum.STATUS_PENDING.value)
    applicant = models.ForeignKey("User",
                                  on_delete=models.DO_NOTHING,
                                  null=True)
    is_active = models.BooleanField(default=True)
