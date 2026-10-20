from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models.deletion import ProtectedError
from django.contrib import messages
from .models import Enfant, Allergie, ContactUrgence, PersonneAutorisee, Groupe, DemandeInscription
from .forms import AllergieForm, ContactUrgenceForm, PersonneAutoriseeForm, GroupeForm, DemandeInscriptionForm

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
    url = reverse("fiche_enfant", args=[enfant.id])

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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
def mon_groupe(request):
    if not request.user.is_educateur:
        raise PermissionDenied(
            "Vous n'avez pas accès à cette page."
        )

    groupes = Groupe.objects.filter(
        educateur__pk=request.user.pk
    ).prefetch_related("enfant_set")

    return render(request, "mon_groupe.html", {
        "groupes": groupes
    })


@login_required
def mes_enfants(request):
    if not request.user.is_parent:
        raise PermissionDenied(
            "Vous n'avez pas accès à cette page."
        )

    enfants = Enfant.objects.filter(
        parents__pk=request.user.pk
    ).select_related("groupe")

    return render(request, "mes_enfants.html", {
        "enfants": enfants
    })


@login_required
def ajouter_groupe(request):
    if not (request.user.is_administrateur or request.user.is_superuser):
        raise PermissionDenied("Vous n'avez pas accès à cette page.")

    form = GroupeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("liste_groupes")

    return render(
        request,
        "groupes/ajouter_groupe.html",
        {"form": form}
    )

@login_required
def liste_groupes(request):
    if not (request.user.is_administrateur or request.user.is_superuser):
        raise PermissionDenied("Vous n'avez pas accès à cette page.")

    groupes = Groupe.objects.select_related("educateur").all()

    return render(
        request,
        "groupes/liste_groupes.html",
        {"groupes": groupes}
    )

@login_required
def modifier_groupe(request, groupe_id):
    if not (request.user.is_administrateur or request.user.is_superuser):
        raise PermissionDenied("Vous n'avez pas accès à cette page.")

    groupe = get_object_or_404(Groupe, id=groupe_id)

    if request.method == "POST":
        form = GroupeForm(request.POST, instance=groupe)

        if form.is_valid():
            form.save()
            return redirect("liste_groupes")
    else:
        form = GroupeForm(instance=groupe)

    return render(
        request,
        "groupes/modifier_groupe.html",
        {
            "form": form,
            "groupe": groupe
        }
    )

@login_required
def supprimer_groupe(request, groupe_id):
    if not (request.user.is_administrateur or request.user.is_superuser):
        raise PermissionDenied("Vous n'avez pas accès à cette page.")

    groupe = get_object_or_404(Groupe, id=groupe_id)

    if request.method == "POST":

        if groupe.enfant_set.exists():
            messages.error(
                request,
                (
                    f'Impossible de supprimer le groupe "{groupe.nom}" '
                    "car il contient encore au moins un enfant. "
                    "Veuillez d'abord réaffecter ou retirer les enfants du groupe."
                )
            )
            return redirect("liste_groupes")

        try:
            nom_groupe = groupe.nom
            groupe.delete()

            messages.success(
                request,
                f'Le groupe "{nom_groupe}" a été supprimé avec succès.'
            )

        except ProtectedError:
            messages.error(
                request,
                f'Impossible de supprimer le groupe "{groupe.nom}".'
            )

        return redirect("liste_groupes")

    return render(
        request,
        "groupes/supprimer_groupe.html",
        {"groupe": groupe}
    )


@login_required
def mes_demandes_inscription(request):
    if not request.user.is_parent:
        raise PermissionDenied(
            "Vous n'avez pas accès à cette page."
        )

    demandes = DemandeInscription.objects.filter(
        parent__pk=request.user.pk
    ).order_by("-date_creation")

    return render(request, "enfants/mes_demandes_inscription.html", {
        "demandes": demandes
    })


@login_required
def creer_demande_inscription(request):
    if not request.user.is_parent:
        raise PermissionDenied(
            "Vous n'avez pas accès à cette page."
        )

    if request.method == "POST":
        form = DemandeInscriptionForm(request.POST)

        if form.is_valid():
            demande = form.save(commit=False)
            demande.parent_id = request.user.pk
            demande.save()

            return redirect("mes_demandes_inscription")

    else:
        form = DemandeInscriptionForm()

    return render(request, "enfants/creer_demande_inscription.html", {
        "form": form
    })


@login_required
def modifier_demande_inscription(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)

    if (
        not request.user.is_parent
        or demande.parent_id != request.user.pk
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de modifier cette demande."
        )

    if demande.statut != DemandeInscription.Statut.EN_ATTENTE:
        raise PermissionDenied(
            "Cette demande a déjà été traitée et ne peut plus être modifiée."
        )

    if request.method == "POST":
        form = DemandeInscriptionForm(request.POST, instance=demande)

        if form.is_valid():
            form.save()

            return redirect("mes_demandes_inscription")

    else:
        form = DemandeInscriptionForm(instance=demande)

    return render(request, "enfants/modifier_demande_inscription.html", {
        "form": form,
        "demande": demande
    })


@login_required
def supprimer_demande_inscription(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)

    if (
        not request.user.is_parent
        or demande.parent_id != request.user.pk
    ):
        raise PermissionDenied(
            "Vous n'avez pas l'autorisation de supprimer cette demande."
        )

    if demande.statut != DemandeInscription.Statut.EN_ATTENTE:
        raise PermissionDenied(
            "Cette demande a déjà été traitée et ne peut plus être supprimée."
        )

    if request.method == "POST":
        demande.delete()

        return redirect("mes_demandes_inscription")

    return render(request, "enfants/supprimer_demande_inscription.html", {
        "demande": demande
    })
