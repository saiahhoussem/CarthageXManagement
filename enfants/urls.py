from django.urls import path
from . import views


urlpatterns = [
    path("enfant/<int:enfant_id>/", views.fiche_enfant, name="fiche_enfant"),
]