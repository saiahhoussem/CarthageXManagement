from django.urls import path
from . import views


urlpatterns = [
    path(
        "enfant/<int:enfant_id>/", 
        views.fiche_enfant, 
        name="fiche_enfant"
    ),

    path(
    "enfant/<int:enfant_id>/allergie/ajouter/",
    views.ajouter_allergie,
    name="ajouter_allergie"
    ),
    
    path(
    "allergie/<int:allergie_id>/modifier/",
    views.modifier_allergie,
    name="modifier_allergie"
    ),
    path(
    "allergie/<int:allergie_id>/supprimer/",
    views.supprimer_allergie,
    name="supprimer_allergie"
    ),
    path(
    "enfant/<int:enfant_id>/contact/ajouter/",
    views.ajouter_contact,
    name="ajouter_contact"
    ),
    path(
    "contact/<int:contact_id>/modifier/",
    views.modifier_contact,
    name="modifier_contact"
    ),
    path(
    "contact/<int:contact_id>/supprimer/",
    views.supprimer_contact,
    name="supprimer_contact"
    ),
    path(
    "enfant/<int:enfant_id>/personne_autorisee/ajouter/",
    views.ajouter_personne_autorisee,
    name="ajouter_personne_autorisee"
    ),
    path(
    "personne_autorisee/<int:personne_id>/modifier/",
    views.modifier_personne_autorisee,
    name="modifier_personne_autorisee"
    ),
    path(
    "personne_autorisee/<int:personne_id>/supprimer/",
    views.supprimer_personne_autorisee,
    name="supprimer_personne_autorisee"
    ),
]

