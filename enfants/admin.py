from django.contrib import admin
from .models import (
    Groupe,
    Enfant,
    Allergie,
    ContactUrgence,
    PersonneAutorisee,
    DemandeInscription,
    Activite,
)


admin.site.register(Groupe)
admin.site.register(Enfant)
admin.site.register(Allergie)
admin.site.register(ContactUrgence)
admin.site.register(PersonneAutorisee)
admin.site.register(DemandeInscription)
admin.site.register(Activite)