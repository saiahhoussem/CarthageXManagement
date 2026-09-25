from django.shortcuts import render, get_object_or_404
from .models import Enfant

def fiche_enfant(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    return render(request, "enfants/fiche_enfant.html", {
        "enfant": enfant
    })

