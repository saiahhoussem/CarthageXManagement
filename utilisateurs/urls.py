from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "utilisateurs"

urlpatterns = [
    path("creer/", views.creer_compte, name="creer_compte"),
    path(
        "deconnexion/",
        auth_views.LogoutView.as_view(next_page="admin:login"),
        name="deconnexion",
    ),
]
