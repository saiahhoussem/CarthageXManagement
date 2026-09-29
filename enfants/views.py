
from django.shortcuts import render, get_object_or_404, redirect

from .models import Enfant, Allergie, ContactUrgence, PersonneAutorisee
from .forms import AllergieForm, ContactUrgenceForm, PersonneAutoriseeForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def obtenir_retour(request):
    retour = request.GET.get("retour")

    if retour not in ["mes-enfants", "mon-groupe"]:
        if request.user.is_parent:
            return "mes-enfants"

        if request.user.is_educateur:
            return "mon-groupe"

    return retour


def rediriger_vers_fiche(enfant, retour):
    url = f"/enfant/{enfant.id}/"

    if retour in ["mes-enfants", "mon-groupe"]:
        url += f"?retour={retour}"

    return redirect(url)


def utilisateur_peut_acceder_enfant(user, enfant):
    if user.is_superuser:
        return True

    if user.is_parent:
        return enfant.parents.filter(pk=user.pk).exists()

    if user.is_educateur:
        return enfant.groupe.educateur_id == user.pk

    return False

@login_required
def fiche_enfant(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    if not utilisateur_peut_acceder_enfant(request.user, enfant):
        raise PermissionDenied(
            "Vous n'avez pas accès à cette fiche d'enfant."
        )

    retour = obtenir_retour(request)

    return render(request, "enfants/fiche_enfant.html", {
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def ajouter_allergie(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        form = AllergieForm(request.POST)

        if form.is_valid():
            allergie = form.save(commit=False)
            allergie.enfant = enfant
            allergie.save()

            return rediriger_vers_fiche(enfant, retour)

    else:
        form = AllergieForm()

    return render(request, "enfants/ajouter_allergie.html", {
        "form": form,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })


def modifier_allergie(request, allergie_id):
    allergie = get_object_or_404(Allergie, id=allergie_id)
    enfant = allergie.enfant

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        form = AllergieForm(request.POST, instance=allergie)

        if form.is_valid():
            form.save()

            return rediriger_vers_fiche(enfant, retour)

    else:
        form = AllergieForm(instance=allergie)

    return render(request, "enfants/modifier_allergie.html", {
        "form": form,
        "allergie": allergie,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def supprimer_allergie(request, allergie_id):
    allergie = get_object_or_404(Allergie, id=allergie_id)
    enfant = allergie.enfant

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        allergie.delete()

        return rediriger_vers_fiche(enfant, retour)

    return render(request, "enfants/supprimer_allergie.html", {
        "allergie": allergie,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def ajouter_contact(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        form = ContactUrgenceForm(request.POST)

        if form.is_valid():
            contact = form.save(commit=False)
            contact.enfant = enfant
            contact.save()

            return rediriger_vers_fiche(enfant, retour)

    else:
        form = ContactUrgenceForm()

    return render(request, "enfants/ajouter_contact.html", {
        "form": form,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def modifier_contact(request, contact_id):
    contact = get_object_or_404(ContactUrgence, id=contact_id)
    enfant = contact.enfant

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        form = ContactUrgenceForm(request.POST, instance=contact)

        if form.is_valid():
            form.save()

            return rediriger_vers_fiche(enfant, retour)

    else:
        form = ContactUrgenceForm(instance=contact)

    return render(request, "enfants/modifier_contact.html", {
        "form": form,
        "contact": contact,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def supprimer_contact(request, contact_id):
    contact = get_object_or_404(ContactUrgence, id=contact_id)
    enfant = contact.enfant

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        contact.delete()

        return rediriger_vers_fiche(enfant, retour)

    return render(request, "enfants/supprimer_contact.html", {
        "contact": contact,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def ajouter_personne_autorisee(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        form = PersonneAutoriseeForm(request.POST)

        if form.is_valid():
            personne = form.save(commit=False)
            personne.enfant = enfant
            personne.save()

            return rediriger_vers_fiche(enfant, retour)

    else:
        form = PersonneAutoriseeForm()

    return render(request, "enfants/ajouter_personne_autorisee.html", {
        "form": form,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def modifier_personne_autorisee(request, personne_id):
    personne = get_object_or_404(PersonneAutorisee, id=personne_id)
    enfant = personne.enfant

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        form = PersonneAutoriseeForm(request.POST, instance=personne)

        if form.is_valid():
            form.save()

            return rediriger_vers_fiche(enfant, retour)

    else:
        form = PersonneAutoriseeForm(instance=personne)

    return render(request, "enfants/modifier_personne_autorisee.html", {
        "form": form,
        "personne": personne,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def supprimer_personne_autorisee(request, personne_id):
    personne = get_object_or_404(PersonneAutorisee, id=personne_id)
    enfant = personne.enfant

    if (
        not request.user.is_parent
        or not utilisateur_peut_acceder_enfant(request.user, enfant)
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette fiche."
        )

    retour = obtenir_retour(request)

    if request.method == "POST":
        personne.delete()

        return rediriger_vers_fiche(enfant, retour)

    return render(request, "enfants/supprimer_personne_autorisee.html", {
        "personne": personne,
        "enfant": enfant,
        "retour": retour,
        "est_parent": request.user.is_parent,
        "est_educateur": request.user.is_educateur,
    })

def mon_groupe(request):
    groupes = request.user.educateur.groupes.prefetch_related("enfant_set")

    return render(request, "mon_groupe.html", {
        "groupes": groupes
    })

def mes_enfants(request):
    enfants = Enfant.objects.filter(
        parents__pk=request.user.pk
    )

    return render(request, "mes_enfants.html", {
        "enfants": enfants
    })
