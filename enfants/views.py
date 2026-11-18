from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count, Prefetch, Q
from django.db.models.deletion import ProtectedError
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal

from .models import (
    Activite,
    Enfant,
    Allergie,
    ContactUrgence,
    PersonneAutorisee,
    Groupe,
    DemandeInscription,
    InscriptionActivite,
    Paiement,
    groupes_pertinents_pour_utilisateur,
    activite_visible_par,
    Presence,
)
from .forms import ActiviteForm, AllergieForm, ContactUrgenceForm, PersonneAutoriseeForm, GroupeForm, DemandeInscriptionForm, AccepterDemandeInscriptionForm, PaiementCarteForm, PresenceParentForm, PresenceEducateurForm, PresenceAdminForm
from compte.models import creer_notification, Parent

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .decorators import (
    administrateur_requis,
    parent_requis,
    educateur_requis,
    educateur_ou_parent_requis,
    verifier_acces_groupe,
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
        or not enfant.actif
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
        or not enfant.actif
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
        or not enfant.actif
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
        or not enfant.actif
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
        or not enfant.actif
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
        or not enfant.actif
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
        or not enfant.actif
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
        or not enfant.actif
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
        or not enfant.actif
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
    enfants_actifs = Enfant.objects.filter(
        actif=True
    ).order_by(
        "nom",
        "prenom"
    )

    groupes = (
        Groupe.objects
        .filter(
            educateur__pk=request.user.pk
        )
        .prefetch_related(
            Prefetch(
                "enfant_set",
                queryset=enfants_actifs
            )
        )
    )

    return render(
        request,
        "mon_groupe.html",
        {
            "groupes": groupes
        }
    )

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
    recherche = request.GET.get("q", "").strip()

    actif = statut != "archives"

    enfants = (
        Enfant.objects
        .filter(actif=actif)
        .select_related("groupe")
    )

    if recherche:
        enfants = enfants.filter(
            Q(prenom__icontains=recherche)
            | Q(nom__icontains=recherche)
        )

    enfants = enfants.order_by("nom", "prenom")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = [
            {
                "id": enfant.id,
                "nom": enfant.nom,
                "prenom": enfant.prenom,
                "date_naissance": enfant.date_naissance.strftime("%Y-%m-%d"),
                "groupe": (
                    enfant.groupe.nom
                    if enfant.groupe
                    else "Non assigné"
                ),
                "actif": enfant.actif,
                "url_detail": reverse(
                    "fiche_enfant",
                    args=[enfant.id],
                ),
                "url_statut": reverse(
                    "basculer_statut_enfant",
                    args=[enfant.id],
                ),
            }
            for enfant in enfants
        ]

        return JsonResponse(
            {
                "enfants": data,
                "statut": statut or "actifs",
                "recherche": recherche,
            }
        )

    return render(
        request,
        "enfants/liste_enfants.html",
        {
            "enfants": enfants,
            "statut": statut or "actifs",
            "recherche": recherche,
        }
    )

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
    recherche = request.GET.get("q", "").strip()

    groupes = (
        Groupe.objects
        .select_related("educateur")
        .order_by("nom")
    )

    if recherche:
        groupes = groupes.filter(
            nom__icontains=recherche
        )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = [
            {
                "id": groupe.id,
                "nom": groupe.nom,
                "tranche_age": groupe.get_tranche_age_display(),
                "capacite": groupe.capacite,
                "educateur": (
                    groupe.educateur.get_full_name()
                    if groupe.educateur
                    else "Non assigné"
                ),
                "places_restantes": groupe.places_restantes,
                "url_detail": reverse(
                    "detail_groupe",
                    args=[groupe.id],
                ),
                "url_modifier": reverse(
                    "modifier_groupe",
                    args=[groupe.id],
                ),
                "url_supprimer": reverse(
                    "supprimer_groupe",
                    args=[groupe.id],
                ),
            }
            for groupe in groupes
        ]

        return JsonResponse({"groupes": data})

    return render(
        request,
        "groupes/liste_groupes.html",
        {
            "groupes": groupes,
            "recherche": recherche,
        }
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

        creer_notification(
            demande.parent,
            f"La demande d'inscription de {demande.prenom_enfant} "
            f"{demande.nom_enfant} a été refusée.",
            reverse("mes_demandes_inscription"),
        )

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

            creer_notification(
                demande.parent,
                f"La demande d'inscription de {demande.prenom_enfant} "
                f"{demande.nom_enfant} a été acceptée.",
                reverse("mes_demandes_inscription"),
            )

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
    recherche = request.GET.get("q", "").strip()

    total_groupes = Groupe.objects.count()

    activites = (
        Activite.objects
        .prefetch_related("groupes")
        .annotate(
            nb_groupes=Count("groupes", distinct=True),
            nb_inscriptions=Count("inscriptions", distinct=True),
        )
        .order_by("date", "heure_debut")
    )

    if recherche:
        activites = activites.filter(
            nom__icontains=recherche
        )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = [
            {
                "id": activite.id,
                "nom": activite.nom,
                "date": activite.date.strftime("%d/%m/%Y"),
                "heure_debut": (
                    activite.heure_debut.strftime("%H:%M")
                    if activite.heure_debut else None
                ),
                "heure_fin": (
                    activite.heure_fin.strftime("%H:%M")
                    if activite.heure_fin else None
                ),
                "plage_horaire": activite.plage_horaire,
                "lieu": activite.lieu,
                "frais": activite.frais_affichage,
                "places_restantes": activite.places_restantes,
                "places_disponibles": activite.places_disponibles,
                "nb_groupes": activite.nb_groupes,
                "total_groupes": total_groupes,
                "groupes": [
                    groupe.nom
                    for groupe in activite.groupes.all()
                ],
                "annulee": activite.annulee,
                "url_detail": reverse(
                    "detail_activite",
                    args=[activite.id],
                ),
                "url_modifier": reverse(
                    "modifier_activite",
                    args=[activite.id],
                ),
                "url_annuler": reverse(
                    "annuler_activite",
                    args=[activite.id],
                ),
                "url_supprimer": reverse(
                    "supprimer_activite",
                    args=[activite.id],
                ),
            }
            for activite in activites
        ]

        return JsonResponse({
            "activites": data
        })

    return render(
        request,
        "activites/liste_activites.html",
        {
            "activites": activites,
            "total_groupes": total_groupes,
            "recherche": recherche,
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
        if activite.inscriptions.exists():
            messages.error(
                request,
                "Impossible de supprimer cette activité : "
                "des enfants y sont inscrits. "
                "Annulez-la plutôt, ou désinscrivez les enfants d'abord."
            )
            return redirect("liste_activites")

        activite.delete()
        messages.success(
            request,
            f"L'activité « {activite.nom} » a été supprimée."
        )
        return redirect("liste_activites")

    return render(
        request,
        "activites/supprimer_activite.html",
        {"activite": activite},
    )

@login_required
@administrateur_requis
def annuler_activite(request, activite_id):
    activite = get_object_or_404(Activite, id=activite_id)

    if activite.annulee:
        raise PermissionDenied(
            "Cette activité est déjà annulée."
        )

    parents_a_notifier = Parent.objects.filter(
        enfants__inscriptions_activites__activite=activite
    ).distinct()

    if request.method == "POST":
        activite.annulee = True
        activite.save(update_fields=["annulee"])

        for parent in parents_a_notifier:
            creer_notification(
                parent,
                f"L'activité « {activite.nom} » du {activite.date:%d/%m/%Y} a été annulée.",
                reverse("detail_activite", args=[activite.id]),
            )

        messages.success(
            request,
            f"L'activité « {activite.nom} » a été annulée et les parents concernés ont été informés."
        )
        return redirect("liste_activites")

    return render(
        request,
        "activites/annuler_activite.html",
        {
            "activite": activite,
            "nb_parents_a_notifier": parents_a_notifier.count(),
        }
    )


@login_required
@educateur_ou_parent_requis
def mes_activites(request):
    recherche = request.GET.get("q", "").strip()

    total_groupes = Groupe.objects.count()

    groupes_pertinents = groupes_pertinents_pour_utilisateur(
        request.user
    )

    toutes_les_activites = (
        Activite.objects
        .exclude(lieu__icontains="garderie")  
        .prefetch_related("groupes")
        .annotate(
            nb_groupes=Count("groupes", distinct=True),
            nb_inscriptions=Count(
                "inscriptions",
                distinct=True
            ),
        )
        .order_by("date")
    )

    activites = [
        activite
        for activite in toutes_les_activites
        if activite_visible_par(
            activite,
            activite.nb_groupes,
            total_groupes,
            groupes_pertinents,
        )
    ]

    if recherche:
        recherche_min = recherche.lower()

        activites = [
            activite
            for activite in activites
            if recherche_min in activite.nom.lower()
        ]

    if (
        request.headers.get("X-Requested-With")
        == "XMLHttpRequest"
    ):
        data = [
            {
                "id": activite.id,
                "nom": activite.nom,
                "date": activite.date.strftime(
                    "%d/%m/%Y"
                ),
                "heure_debut": (                                   
                    activite.heure_debut.strftime("%H:%M")
                    if activite.heure_debut else None
                ),
                "heure_fin": (                                      
                    activite.heure_fin.strftime("%H:%M")
                    if activite.heure_fin else None
                ),
                "photo_url": activite.photo_url,
                "lieu": activite.lieu,
                "description": activite.description,
                "places_restantes": (
                    activite.places_restantes
                ),
                "frais_affichage": (
                    activite.frais_affichage
                ),
                "groupes": [
                    {
                        "id": groupe.id,
                        "nom": groupe.nom,
                    }
                    for groupe
                    in activite.groupes.all()
                ],
                "nb_groupes": activite.nb_groupes,
                "total_groupes": total_groupes,
                "annulee": activite.annulee,
            }
            for activite in activites
        ]

        return JsonResponse({
            "activites": data
        })

    return render(
        request,
        "activites/mes_activites.html",
        {
            "activites": activites,
            "total_groupes": total_groupes,
            "recherche": recherche,
        }
    )

@login_required
def detail_activite(request, activite_id):
    activite = get_object_or_404(
        Activite.objects.prefetch_related("groupes", "inscriptions__enfant")
        .annotate(
            nb_groupes=Count("groupes", distinct=True),
            nb_inscriptions=Count("inscriptions", distinct=True),
        ),
        id=activite_id,
    )

    est_admin = request.user.is_superuser or request.user.is_administrateur

    if not est_admin:
        total_groupes = Groupe.objects.count()
        groupes_pertinents = groupes_pertinents_pour_utilisateur(request.user)

        if not activite_visible_par(
            activite, activite.nb_groupes, total_groupes, groupes_pertinents
        ):
            raise PermissionDenied(
                "Cette activité ne concerne pas votre groupe."
            )

    contexte = {"activite": activite}

    if est_admin:
        contexte["inscriptions"] = activite.inscriptions.all()
    elif request.user.is_parent:
        groupes_ids_activite = {groupe.pk for groupe in activite.groupes.all()}

        enfants_eligibles = [
            enfant
            for enfant in Enfant.objects.filter(
                parents__pk=request.user.pk, actif=True
            ).select_related("groupe")
            if activite.applique_a_tous_les_groupes
            or enfant.groupe_id in groupes_ids_activite
        ]

        inscriptions_existantes = {
            inscription.enfant_id: inscription
            for inscription in activite.inscriptions.all()
        }

        contexte["enfants_inscription"] = [
            {
                "enfant": enfant,
                "inscription": inscriptions_existantes.get(enfant.id),
            }
            for enfant in enfants_eligibles
        ]

    return render(
        request,
        "activites/detail_activite.html",
        contexte,
    )

@login_required
@parent_requis
def signaler_presence(request):
    parent = request.user.parent

    if request.method == "POST":
        form = PresenceParentForm(
            request.POST,
            parent=parent
        )

        if form.is_valid():
            presence = form.save(commit=False)

            presence.parent = parent
            presence.source_signalement = Presence.SourceSignalement.PARENT

            presence.save()

            messages.success(
                request,
                "Le signalement a bien été enregistré."
            )

            return redirect("historique_presences_parent")

    else:
        form = PresenceParentForm(
            parent=parent
        )

    return render(
        request,
        "presences/signaler_presence.html",
        {
            "form": form,
        }
    )

@login_required
@parent_requis
def historique_presences_parent(request):
    parent = request.user.parent
    recherche = request.GET.get("q", "").strip()
    today = timezone.localdate()

    presences = (
        Presence.objects
        .filter(parent=parent)
        .select_related("enfant")
        .order_by("-date_signalement")
    )

    if recherche:
        presences = presences.filter(
            Q(enfant__prenom__icontains=recherche)
            | Q(enfant__nom__icontains=recherche)
        )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = []

        for presence in presences:
            date_limite = presence.date_fin or presence.date

            data.append(
                {
                    "id": presence.id,
                    "enfant": (
                        f"{presence.enfant.prenom} "
                        f"{presence.enfant.nom}"
                    ),
                    "type": presence.get_type_display(),
                    "date": presence.date.strftime("%d/%m/%Y"),
                    "date_fin": (
                        presence.date_fin.strftime("%d/%m/%Y")
                        if presence.date_fin
                        else ""
                    ),
                    "heure": presence.heure.strftime("%H:%M"),
                    "heure_fin": (
                        presence.heure_fin.strftime("%H:%M")
                        if presence.heure_fin
                        else ""
                    ),
                    "motif": presence.motif,
                    "source": (
                        presence.get_source_signalement_display()
                    ),
                    "date_signalement": (
                        timezone.localtime(
                            presence.date_signalement
                        ).strftime("%d/%m/%Y %H:%M")
                    ),
                    "modifiable": date_limite >= today,
                    "url_modifier": reverse(
                        "modifier_presence_parent",
                        args=[presence.id],
                    ),
                    "url_supprimer": reverse(
                        "supprimer_presence_parent",
                        args=[presence.id],
                    ),
                }
            )

        return JsonResponse({
            "presences": data
        })

    return render(
        request,
        "presences/historique_parent.html",
        {
            "presences": presences,
            "today": today,
            "recherche": recherche,
        }
    )


@login_required
@educateur_requis
def enregistrer_presence(request):
    educateur = request.user.educateur

    enfant_id = request.GET.get("enfant")

    if request.method == "POST":
        form = PresenceEducateurForm(
            request.POST,
            educateur=educateur
        )

        if form.is_valid():
            presence = form.save(commit=False)

            presence.educateur = educateur
            presence.source_signalement = (
                Presence.SourceSignalement.EDUCATEUR
            )

            presence.save()

            messages.success(
                request,
                "La présence a bien été enregistrée."
            )

            # Retour direct au groupe pour continuer rapidement
            # la prise de présence.
            return redirect("mon_groupe")

    else:
        maintenant = timezone.localtime()

        initial = {
            "type": Presence.Type.ABSENCE,
            "date": maintenant.date(),
            "heure": maintenant.time().replace(
                second=0,
                microsecond=0
            ),
            "motif": "RAS",
        }

        if enfant_id:
            initial["enfant"] = enfant_id

        form = PresenceEducateurForm(
            educateur=educateur,
            initial=initial
        )

    return render(
        request,
        "presences/enregistrer_presence.html",
        {
            "form": form
        }
    )

@login_required
@administrateur_requis
def enregistrer_presence_admin(request):

    if request.method == "POST":
        form = PresenceAdminForm(request.POST)

        if form.is_valid():
            presence = form.save(commit=False)

            presence.source_signalement = (
                Presence.SourceSignalement.ADMINISTRATEUR
            )

            presence.save()

            messages.success(
                request,
                "L'absence ou le retard a bien été enregistré."
            )

            return redirect("registre_presences")

    else:
        form = PresenceAdminForm()

    return render(
        request,
        "presences/enregistrer_presence_admin.html",
        {
            "form": form,
        }
    )


@login_required
@administrateur_requis
def modifier_presence_admin(request, presence_id):
    presence = get_object_or_404(
        Presence,
        id=presence_id
    )

    if request.method == "POST":
        form = PresenceAdminForm(
            request.POST,
            instance=presence
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Le signalement a bien été modifié."
            )

            return redirect("registre_presences")

    else:
        form = PresenceAdminForm(
            instance=presence
        )

    return render(
        request,
        "presences/modifier_presence_admin.html",
        {
            "form": form,
            "presence": presence,
        }
    )


@login_required
@administrateur_requis
def supprimer_presence_admin(request, presence_id):
    presence = get_object_or_404(
        Presence,
        id=presence_id
    )

    if request.method == "POST":
        presence.delete()

        messages.success(
            request,
            "Le signalement a bien été supprimé."
        )

        return redirect("registre_presences")

    return render(
        request,
        "presences/supprimer_presence_admin.html",
        {
            "presence": presence,
        }
    )



@login_required
@educateur_requis
def historique_presences_educateur(request):
    educateur = request.user.educateur

    presences = (
        Presence.objects
        .filter(enfant__groupe__educateur=educateur)
        .select_related("enfant")
        .order_by("-date", "-heure")
    )

    return render(
        request,
        "presences/historique_educateur.html",
        {
            "presences": presences,
        }
    )


@login_required
@administrateur_requis
def registre_presences(request):
    presences = (
        Presence.objects
        .select_related(
            "enfant",
            "enfant__groupe",
        )
        .order_by("-date", "-heure")
    )

    groupe_id = request.GET.get("groupe")
    date = request.GET.get("date")
    enfant_id = request.GET.get("enfant")

    if groupe_id:
        presences = presences.filter(
            enfant__groupe_id=groupe_id
        )

    if date:
        presences = presences.filter(
            date=date
        )

    if enfant_id:
        presences = presences.filter(
            enfant_id=enfant_id
        )

    groupes = Groupe.objects.order_by("nom")

    enfants = Enfant.objects.order_by(
        "nom",
        "prenom"
    )

    if groupe_id:
        enfants = enfants.filter(
            groupe_id=groupe_id
        )

    return render(
        request,
        "presences/registre_presences.html",
        {
            "presences": presences,
            "groupes": groupes,
            "enfants": enfants,
            "groupe_selectionne": groupe_id,
            "date_selectionnee": date,
            "enfant_selectionne": enfant_id,
        }
    )



@login_required
@parent_requis
def modifier_presence_parent(request, presence_id):
    parent = request.user.parent

    presence = get_object_or_404(
        Presence,
        id=presence_id,
        parent=parent
    )

    date_limite = presence.date_fin or presence.date

    if date_limite < timezone.now().date():
        messages.error(
            request,
            "Ce signalement ne peut plus être modifié, car sa période est terminée."
        )
        return redirect("historique_presences_parent")

    if request.method == "POST":
        form = PresenceParentForm(
            request.POST,
            instance=presence,
            parent=parent
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Le signalement a bien été modifié."
            )

            return redirect("historique_presences_parent")

    else:
        form = PresenceParentForm(
            instance=presence,
            parent=parent
        )

    return render(
        request,
        "presences/modifier_presence_parent.html",
        {
            "form": form,
            "presence": presence,
        }
    )

@login_required
@parent_requis
def inscrire_activite(request, activite_id):
    activite = get_object_or_404(Activite, id=activite_id)

    if request.method != "POST":
        return redirect("detail_activite", activite_id=activite.id)

    enfant = get_object_or_404(
        Enfant,
        id=request.POST.get("enfant_id"),
        parents__pk=request.user.pk,
        actif=True,
    )

    groupes_ids_activite = {groupe.pk for groupe in activite.groupes.all()}

    if not (
        activite.applique_a_tous_les_groupes
        or enfant.groupe_id in groupes_ids_activite
    ):
        raise PermissionDenied(
            "Cette activité ne concerne pas le groupe de cet enfant."
        )

    if activite.annulee:
        messages.error(
            request,
            f"L'activité « {activite.nom} » a été annulée, les inscriptions ne sont plus possibles."
        )
    elif InscriptionActivite.objects.filter(activite=activite, enfant=enfant).exists():
        messages.info(
            request,
            f"{enfant} est déjà inscrit(e) à l'activité « {activite.nom} »."
        )
    elif activite.places_restantes <= 0:
        messages.error(
            request,
            f"L'activité « {activite.nom} » est complète, il ne reste plus de place disponible."
        )
    else:
        InscriptionActivite.objects.create(activite=activite, enfant=enfant)
        messages.success(
            request,
            f"{enfant} a été inscrit(e) à l'activité « {activite.nom} »."
        )

    return redirect("detail_activite", activite_id=activite.id)


@login_required
@parent_requis
def supprimer_presence_parent(request, presence_id):
    parent = request.user.parent

    presence = get_object_or_404(
        Presence,
        id=presence_id,
        parent=parent
    )

    date_limite = presence.date_fin or presence.date

    if date_limite < timezone.now().date():
        messages.error(
            request,
            "Ce signalement ne peut plus être supprimé, car sa période est terminée."
        )
        return redirect("historique_presences_parent")

    if request.method == "POST":
        presence.delete()

        messages.success(
            request,
            "Le signalement a bien été supprimé."
        )

        return redirect("historique_presences_parent")

    return render(
        request,
        "presences/supprimer_presence_parent.html",
        {
            "presence": presence,
        }
    )

@login_required
@administrateur_requis
def enfants_par_groupe(request):
    groupe_id = request.GET.get("groupe")

    enfants = Enfant.objects.filter(
        groupe_id=groupe_id
    ).order_by("nom", "prenom")

    data = [
        {
            "id": enfant.id,
            "nom": f"{enfant.prenom} {enfant.nom}"
        }
        for enfant in enfants
    ]

    return JsonResponse(
        {
            "enfants": data
        }
    )



@login_required
@educateur_requis
def modifier_presence_educateur(request, presence_id):
    educateur = request.user.educateur

    presence = get_object_or_404(
        Presence,
        id=presence_id,
        educateur=educateur,
        enfant__groupe__educateur=educateur,
    )

    if request.method == "POST":
        form = PresenceEducateurForm(
            request.POST,
            instance=presence,
            educateur=educateur,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Le signalement a bien été modifié."
            )

            return redirect(
                "historique_presences_educateur"
            )

    else:
        form = PresenceEducateurForm(
            instance=presence,
            educateur=educateur,
        )

    return render(
        request,
        "presences/modifier_presence_educateur.html",
        {
            "form": form,
            "presence": presence,
        }
    )


@login_required
@educateur_requis
def supprimer_presence_educateur(request, presence_id):
    educateur = request.user.educateur

    presence = get_object_or_404(
        Presence,
        id=presence_id,
        educateur=educateur,
        enfant__groupe__educateur=educateur,
    )

    if request.method == "POST":
        presence.delete()

        messages.success(
            request,
            "Le signalement a bien été supprimé."
        )

        return redirect(
            "historique_presences_educateur"
        )

    return render(
        request,
        "presences/supprimer_presence_educateur.html",
        {
            "presence": presence,
        }
    )


def desinscrire_activite(request, inscription_id):
    inscription = get_object_or_404(
        InscriptionActivite,
        id=inscription_id,
        enfant__parents__pk=request.user.pk,
    )

    if request.method == "POST":
        if hasattr(inscription, "paiement"):
            messages.error(
                request,
                f"Impossible de se désinscrire de « {inscription.activite.nom} » : "
                "les frais d'inscription ont déjà été payés."
            )
            return redirect("detail_activite", activite_id=inscription.activite_id)

        activite_id = inscription.activite_id
        enfant = inscription.enfant
        nom_activite = inscription.activite.nom
        inscription.delete()

        messages.success(
            request,
            f"{enfant} a été désinscrit(e) de l'activité « {nom_activite} »."
        )
        return redirect("detail_activite", activite_id=activite_id)

    return redirect("detail_activite", activite_id=inscription.activite_id)


@login_required
@parent_requis
def payer_inscription(request, inscription_id):
    inscription = get_object_or_404(
        InscriptionActivite,
        id=inscription_id,
        enfant__parents__pk=request.user.pk,
    )
    activite = inscription.activite

    if activite.frais_inscription <= 0:
        messages.info(
            request,
            f"L'activité « {activite.nom} » est gratuite, aucun paiement n'est requis."
        )
        return redirect("detail_activite", activite_id=activite.id)

    if hasattr(inscription, "paiement"):
        messages.info(
            request,
            f"Les frais d'inscription de « {activite.nom} » ont déjà été payés."
        )
        return redirect("detail_activite", activite_id=activite.id)

    if request.method == "POST":
        form = PaiementCarteForm(request.POST)

        if form.is_valid():
            Paiement.objects.create(
                inscription=inscription,
                parent=request.user.parent,
                montant=activite.frais_inscription,
            )

            messages.success(
                request,
                f"Le paiement de {activite.frais_inscription} $ pour « {activite.nom} » a été effectué avec succès."
            )
            return redirect("detail_activite", activite_id=activite.id)
    else:
        form = PaiementCarteForm()

    return render(request, "activites/payer_inscription.html", {
        "inscription": inscription,
        "activite": activite,
        "form": form,
    })


@login_required
@parent_requis
def historique_paiements_parent(request):
    paiements = (
        Paiement.objects
        .filter(parent=request.user.parent)
        .select_related("inscription__activite", "inscription__enfant")
        .order_by("-date_paiement")
    )

    montant_total = sum(
        (paiement.montant for paiement in paiements),
        Decimal("0"),
    )

    return render(request, "paiements/historique_parent.html", {
        "paiements": paiements,
        "montant_total": montant_total,
    })


@login_required
@administrateur_requis
def detail_groupe(request, groupe_id):
    groupe = get_object_or_404(
        Groupe.objects.select_related("educateur"),
        id=groupe_id,
    )

    enfants = (
        Enfant.objects
        .filter(groupe=groupe)
        .order_by("nom", "prenom")
    )

    return render(
        request,
        "groupes/detail_groupe.html",
        {
            "groupe": groupe,
            "enfants": enfants,
        }
    )


@login_required
def horaire_groupe(request, groupe_id):
    groupe = get_object_or_404(
        Groupe.objects.select_related("educateur"),
        id=groupe_id,
    )

    verifier_acces_groupe(request.user, groupe)

    aujourd_hui = timezone.localdate()
    fin = aujourd_hui + timedelta(days=90)

    activites = (
        Activite.objects
        .filter(annulee=False)
        .filter(date__gte=aujourd_hui, date__lte=fin)
        .filter(
            Q(groupes=groupe) | Q(groupes__isnull=True)
        )
        .distinct()
        .prefetch_related("groupes")
        .order_by("date", "heure_debut")
    )

    horaire = {}
    for activite in activites:
        horaire.setdefault(activite.date, []).append(activite)

    horaire = dict(sorted(horaire.items()))

    return render(
        request,
        "enfants/horaire_groupe.html",
        {
            "groupe": groupe,
            "horaire": horaire,
            "nb_activites": len(activites),
            "aujourd_hui": aujourd_hui,
            "titre_page": f"Horaire – {groupe.nom}",
        },
    )


@login_required
@parent_requis
def horaire_parent(request):
    mes_enfants = (
        Enfant.objects
        .filter(parents=request.user, actif=True)
        .select_related("groupe")
        .order_by("prenom", "nom")
    )

    enfant_id = request.GET.get("enfant")

    if enfant_id:
        enfant = get_object_or_404(mes_enfants, id=enfant_id)
        return redirect("horaire_groupe", groupe_id=enfant.groupe_id)

    return render(
        request,
        "enfants/horaire_parent.html",
        {
            "mes_enfants": mes_enfants,
            "titre_page": "Calendrier de mes enfants",
        },
    )


@login_required
@administrateur_requis
def horaire_admin(request):
    """
    Page de sélection : liste tous les groupes avec accès à leur horaire.
    """
    groupes = (
        Groupe.objects
        .select_related("educateur")
        .prefetch_related("enfant_set")
        .order_by("nom")
    )

    aujourd_hui = timezone.localdate()
    fin = aujourd_hui + timedelta(days=90)

    groupes_data = []
    for groupe in groupes:
        nb_activites = (
            Activite.objects
            .filter(annulee=False)
            .filter(date__gte=aujourd_hui, date__lte=fin)
            .filter(
                Q(groupes=groupe) | Q(groupes__isnull=True)
            )
            .distinct()
            .count()
        )
        groupes_data.append({
            "groupe": groupe,
            "nb_activites": nb_activites,
            "nb_enfants": groupe.enfant_set.count(),
        })

    return render(
        request,
        "enfants/horaire_admin.html",
        {
            "groupes_data": groupes_data,
            "titre_page": "Calendrier de tous les groupes",
        },
    )
