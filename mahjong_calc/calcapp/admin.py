from django.contrib import admin
from .models import Calculation

@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ("id","user","created_at","hand_text","win_tile_text")
