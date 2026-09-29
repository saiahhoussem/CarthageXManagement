from django.shortcuts import render, get_object_or_404, redirect
from .models import Enfant, Allergie, ContactUrgence, PersonneAutorisee
from .forms import AllergieForm, ContactUrgenceForm, PersonneAutoriseeForm

def fiche_enfant(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    return render(request, "enfants/fiche_enfant.html", {
        "enfant": enfant
    })

def ajouter_allergie(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    if request.method == "POST":
        form = AllergieForm(request.POST)

        if form.is_valid():
            allergie = form.save(commit=False)
            allergie.enfant = enfant
            allergie.save()

            return redirect("fiche_enfant", enfant_id=enfant.id)

    else:
        form = AllergieForm()

    return render(request, "enfants/ajouter_allergie.html", {
        "form": form,
        "enfant": enfant
    })

    
def modifier_allergie(request, allergie_id):
    allergie = get_object_or_404(Allergie, id=allergie_id)

    if request.method == "POST":
        form = AllergieForm(request.POST, instance=allergie)

        if form.is_valid():
            form.save()

            return redirect(
                "fiche_enfant",
                enfant_id=allergie.enfant.id
            )

    else:
        form = AllergieForm(instance=allergie)

    return render(request, "enfants/modifier_allergie.html", {
        "form": form,
        "allergie": allergie,
        "enfant": allergie.enfant
    })

def supprimer_allergie(request, allergie_id):
    allergie = get_object_or_404(Allergie, id=allergie_id)

    if request.method == "POST":
        enfant_id = allergie.enfant.id
        allergie.delete()

        return redirect("fiche_enfant", enfant_id=enfant_id)

    return render(request, "enfants/supprimer_allergie.html", {
        "allergie": allergie,
        "enfant": allergie.enfant
    })


def ajouter_contact(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    if request.method == "POST":
        form = ContactUrgenceForm(request.POST)

        if form.is_valid():
            contact = form.save(commit=False)
            contact.enfant = enfant
            contact.save()

            return redirect("fiche_enfant", enfant_id=enfant.id)

    else:
        form = ContactUrgenceForm()

    return render(request, "enfants/ajouter_contact.html", {
        "form": form,
        "enfant": enfant
    })

def modifier_contact(request, contact_id):
    contact = get_object_or_404(ContactUrgence, id=contact_id)

    if request.method == "POST":
        form = ContactUrgenceForm(request.POST, instance=contact)

        if form.is_valid():
            form.save()

            return redirect(
                "fiche_enfant",
                enfant_id=contact.enfant.id
            )

    else:
        form = ContactUrgenceForm(instance=contact)

    return render(request, "enfants/modifier_contact.html", {
        "form": form,
        "contact": contact,
        "enfant": contact.enfant
    })

def supprimer_contact(request, contact_id):
    contact = get_object_or_404(ContactUrgence, id=contact_id)

    if request.method == "POST":
        enfant_id = contact.enfant.id
        contact.delete()

        return redirect("fiche_enfant", enfant_id=enfant_id)

    return render(request, "enfants/supprimer_contact.html", {
        "contact": contact,
        "enfant": contact.enfant
    })

def ajouter_personne_autorisee(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    if request.method == "POST":
        form = PersonneAutoriseeForm(request.POST)

        if form.is_valid():
            personne = form.save(commit=False)
            personne.enfant = enfant
            personne.save()

            return redirect("fiche_enfant", enfant_id=enfant.id)

    else:
        form = PersonneAutoriseeForm()

    return render(request, "enfants/ajouter_personne_autorisee.html", {
        "form": form,
        "enfant": enfant
    })

def modifier_personne_autorisee(request, personne_id):
    personne = get_object_or_404(PersonneAutorisee, id=personne_id)

    if request.method == "POST":
        form = PersonneAutoriseeForm(request.POST, instance=personne)

        if form.is_valid():
            form.save()

            return redirect(
                "fiche_enfant",
                enfant_id=personne.enfant.id
            )

    else:
        form = PersonneAutoriseeForm(instance=personne)

    return render(request, "enfants/modifier_personne_autorisee.html", {
        "form": form,
        "personne": personne,
        "enfant": personne.enfant
    })

def supprimer_personne_autorisee(request, personne_id):
    personne = get_object_or_404(PersonneAutorisee, id=personne_id)

    if request.method == "POST":
        enfant_id = personne.enfant.id
        personne.delete()

        return redirect("fiche_enfant", enfant_id=enfant_id)

    return render(request, "enfants/supprimer_personne_autorisee.html", {
        "personne": personne,
        "enfant": personne.enfant
    })