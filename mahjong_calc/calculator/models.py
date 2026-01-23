from django.db import models
from django.contrib.auth.models import User

class CalculationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hand_image = models.JSONField(verbose_name="Hand Configuration") # JSON storing tiles info
    result_data = models.JSONField(verbose_name="Calculation Result") # JSON storing Han, Fu, Points, Yaku
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
