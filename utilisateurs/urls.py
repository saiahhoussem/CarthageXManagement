from django.urls import path

from . import views

app_name = "utilisateurs"

urlpatterns = [
    path("creer/", views.creer_compte, name="creer_compte"),
]
