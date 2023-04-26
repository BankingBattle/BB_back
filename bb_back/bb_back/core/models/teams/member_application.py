from django.db import models

from bb_back.core.constants import TeamApplicationStatusesEnum


class MemberApplication(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    applicant = models.ForeignKey("User", on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(
        default=TeamApplicationStatusesEnum.STATUS_PENDING.value)
