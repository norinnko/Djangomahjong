from django.conf import settings
from django.db import models

class Calculation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="calculations")
    hand_text = models.CharField(max_length=200)
    win_tile_text = models.CharField(max_length=10)
    melds_json = models.JSONField(default=list, blank=True)
    config_json = models.JSONField(default=dict, blank=True)
    result_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
