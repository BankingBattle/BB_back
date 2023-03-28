from django.db import models


class Team(models.Model):
    game = models.ForeignKey("Game", on_delete=models.DO_NOTHING, null=True)
    name = models.CharField(max_length=63)
    description = models.TextField(null=True)
    application = models.ForeignKey("TeamApplication",
                                    on_delete=models.DO_NOTHING,
                                    null=True)

    is_active = models.BooleanField(default=True)
