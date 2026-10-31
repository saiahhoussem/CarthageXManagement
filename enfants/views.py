from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.contrib import messages
from .models import (
    Activite,
    Enfant,
    Allergie,
    ContactUrgence,
    PersonneAutorisee,
    Groupe,
    DemandeInscription,
    groupes_pertinents_pour_utilisateur,
    activite_visible_par,
)
from .forms import ActiviteForm, AllergieForm, ContactUrgenceForm, PersonneAutoriseeForm, GroupeForm, DemandeInscriptionForm, AccepterDemandeInscriptionForm

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .decorators import (
    administrateur_requis,
    parent_requis,
    educateur_requis,
    educateur_ou_parent_requis,
)


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
    if user.is_superuser or user.is_administrateur:
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
@educateur_requis
def mon_groupe(request):

    groupes = Groupe.objects.filter(
        educateur__pk=request.user.pk
    ).prefetch_related("enfant_set")

    return render(request, "mon_groupe.html", {
        "groupes": groupes
    })


@login_required
@parent_requis
def mes_enfants(request):

    enfants = Enfant.objects.filter(
        parents__pk=request.user.pk,
        actif=True,
    ).select_related("groupe")

    return render(request, "mes_enfants.html", {
        "enfants": enfants
    })


@login_required
@administrateur_requis
def liste_enfants(request):
    statut = request.GET.get("statut")
    actif = statut != "archives"

    enfants = (
        Enfant.objects
        .filter(actif=actif)
        .select_related("groupe")
        .order_by("nom", "prenom")
    )

    return render(request, "enfants/liste_enfants.html", {
        "enfants": enfants,
        "statut": statut or "actifs",
    })


@login_required
@administrateur_requis
def basculer_statut_enfant(request, enfant_id):
    enfant = get_object_or_404(Enfant, id=enfant_id)

    if request.method != "POST":
        return redirect("fiche_enfant", enfant_id=enfant.id)

    enfant.actif = not enfant.actif
    enfant.save(update_fields=["actif"])

    if enfant.actif:
        messages.success(request, f"Le dossier de {enfant} a été réactivé.")
    else:
        messages.success(request, f"Le dossier de {enfant} a été archivé.")

    return redirect("fiche_enfant", enfant_id=enfant.id)


@login_required
@administrateur_requis
def ajouter_groupe(request):
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
@administrateur_requis
def liste_groupes(request):
    groupes = Groupe.objects.select_related("educateur").all()

    return render(
        request,
        "groupes/liste_groupes.html",
        {"groupes": groupes}
    )

@login_required
@administrateur_requis
def modifier_groupe(request, groupe_id):
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
@administrateur_requis
def supprimer_groupe(request, groupe_id):
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
@parent_requis
def mes_demandes_inscription(request):

    demandes = DemandeInscription.objects.filter(
        parent__pk=request.user.pk
    ).order_by("-date_creation")

    return render(request, "enfants/mes_demandes_inscription.html", {
        "demandes": demandes
    })


@login_required
@parent_requis
def creer_demande_inscription(request):

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


@login_required
@administrateur_requis
def liste_demandes_inscription(request):
    demandes = DemandeInscription.objects.select_related("parent").order_by(
        "-date_creation"
    )

    return render(request, "enfants/liste_demandes_inscription.html", {
        "demandes": demandes
    })


@login_required
@administrateur_requis
def detail_demande_inscription(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)

    return render(request, "enfants/detail_demande_inscription.html", {
        "demande": demande
    })


@login_required
@administrateur_requis
def refuser_demande_inscription(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)

    if demande.statut != DemandeInscription.Statut.EN_ATTENTE:
        raise PermissionDenied(
            "Cette demande a déjà été traitée et ne peut plus être refusée."
        )

    if request.method == "POST":
        demande.statut = DemandeInscription.Statut.REFUSEE
        demande.save(update_fields=["statut", "date_modification"])

        messages.success(
            request,
            f"La demande d'inscription de {demande.prenom_enfant} "
            f"{demande.nom_enfant} a été refusée."
        )

    return redirect("detail_demande_inscription", demande_id=demande.id)


@login_required
@administrateur_requis
def accepter_demande_inscription(request, demande_id):
    demande = get_object_or_404(DemandeInscription, id=demande_id)

    if demande.statut != DemandeInscription.Statut.EN_ATTENTE:
        raise PermissionDenied(
            "Cette demande a déjà été traitée et ne peut plus être acceptée."
        )

    if request.method == "POST":
        form = AccepterDemandeInscriptionForm(request.POST)

        if form.is_valid():
            groupe = form.cleaned_data["groupe"]

            enfant = Enfant(
                prenom=demande.prenom_enfant,
                nom=demande.nom_enfant,
                date_naissance=demande.date_naissance,
                groupe=groupe,
            )
            enfant.full_clean()
            enfant.save()
            enfant.parents.add(demande.parent)

            demande.statut = DemandeInscription.Statut.APPROUVEE
            demande.save(update_fields=["statut", "date_modification"])

            messages.success(
                request,
                f"La demande d'inscription de {demande.prenom_enfant} "
                f"{demande.nom_enfant} a été acceptée et l'enfant a été "
                f"ajouté au groupe {groupe.nom}."
            )
            return redirect("detail_demande_inscription", demande_id=demande.id)
    else:
        form = AccepterDemandeInscriptionForm()

    return render(request, "enfants/accepter_demande_inscription.html", {
        "form": form,
        "demande": demande,
    })


@login_required
@administrateur_requis
def ajouter_activite(request):

    form = ActiviteForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            f"L'activité « {form.cleaned_data['nom']} » a été créée avec succès."
        )
        return redirect("liste_activites")

    return render(
        request,
        "activites/ajouter_activite.html",
        {"form": form}
    )


@login_required
@administrateur_requis
def liste_activites(request):
    activites = (
        Activite.objects
        .prefetch_related("groupes")
        .annotate(nb_groupes=Count("groupes"))
        .order_by("date")
    )

    return render(
        request,
        "activites/liste_activites.html",
        {
            "activites": activites,
            "total_groupes": Groupe.objects.count(),
        }
    )


@login_required
@administrateur_requis
def modifier_activite(request, activite_id):
    activite = get_object_or_404(Activite, id=activite_id)

    if request.method == "POST":
        form = ActiviteForm(request.POST, request.FILES, instance=activite)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"L'activité « {activite.nom} » a été modifiée avec succès."
            )
            return redirect("liste_activites")
    else:
        form = ActiviteForm(instance=activite)

    return render(
        request,
        "activites/modifier_activite.html",
        {
            "form": form,
            "activite": activite,
        }
    )


@login_required
@administrateur_requis
def supprimer_activite(request, activite_id):
    activite = get_object_or_404(Activite, id=activite_id)

    if request.method == "POST":
        nom_activite = activite.nom
        activite.delete()

        messages.success(
            request,
            f"L'activité « {nom_activite} » a été supprimée avec succès."
        )
        return redirect("liste_activites")

    return render(
        request,
        "activites/supprimer_activite.html",
        {"activite": activite}
    )


@login_required
@educateur_ou_parent_requis
def mes_activites(request):
    total_groupes = Groupe.objects.count()
    groupes_pertinents = groupes_pertinents_pour_utilisateur(request.user)

    toutes_les_activites = (
        Activite.objects
        .prefetch_related("groupes")
        .annotate(nb_groupes=Count("groupes"))
        .order_by("date")
    )

    # Filtré en Python (pas en SQL) pour pouvoir réutiliser nb_groupes/
    # total_groupes déjà annotés/calculés, sans requête supplémentaire par
    # activité ni double comptage via une jointure sur groupes.
    activites = [
        activite
        for activite in toutes_les_activites
        if activite_visible_par(
            activite, activite.nb_groupes, total_groupes, groupes_pertinents
        )
    ]

    return render(
        request,
        "activites/mes_activites.html",
        {
            "activites": activites,
            "total_groupes": total_groupes,
        }
    )


@login_required
@educateur_ou_parent_requis
def detail_activite(request, activite_id):
    activite = get_object_or_404(
        Activite.objects.prefetch_related("groupes")
        .annotate(nb_groupes=Count("groupes")),
        id=activite_id,
    )

    total_groupes = Groupe.objects.count()
    groupes_pertinents = groupes_pertinents_pour_utilisateur(request.user)

    if not activite_visible_par(
        activite, activite.nb_groupes, total_groupes, groupes_pertinents
    ):
        raise PermissionDenied(
            "Cette activité ne concerne pas votre groupe."
        )

    return render(
        request,
        "activites/detail_activite.html",
        {"activite": activite}
    )
