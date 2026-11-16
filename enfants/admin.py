from django.contrib import admin
from .models import (
    Groupe,
    Enfant,
    Allergie,
    ContactUrgence,
    PersonneAutorisee,
    DemandeInscription,
    Activite,
    InscriptionActivite,
)


admin.site.register(Groupe)
admin.site.register(Enfant)
admin.site.register(Allergie)
admin.site.register(ContactUrgence)
admin.site.register(PersonneAutorisee)
admin.site.register(DemandeInscription)


@admin.register(InscriptionActivite)
class InscriptionActiviteAdmin(admin.ModelAdmin):
    list_display = ["enfant", "activite", "date_inscription"]


@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ["nom", "date", "lieu", "frais_inscription", "places_disponibles"]