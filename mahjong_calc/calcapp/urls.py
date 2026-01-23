from django.urls import path
from . import views

app_name = "calcapp"
urlpatterns = [
    path("", views.home, name="home"),
    path("history/", views.history_list, name="history_list"),
    path("history/<int:pk>/", views.history_detail, name="history_detail"),
    path("history/<int:pk>/delete/", views.history_delete, name="history_delete"),
]
