from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, ProtectedError
from django.shortcuts import redirect, render, get_object_or_404
from .models import Administrateur, Educateur, User, Parent, Notification, est_administrateur
from .forms import ConnexionForm, CreationAdministrateurForm, ModificationAdministrateurForm, CreationEducateurForm, ModificationEducateurForm, CreationParentForm, ModificationParentForm
from django.utils import timezone
from django.http import JsonResponse
from enfants.models import Enfant, Groupe, Activite
from enfants.decorators import administrateur_requis
from django.urls import reverse

from enfants.models import (
    Activite,
    Enfant,
    Groupe,
    groupes_pertinents_pour_utilisateur,
    activite_visible_par,
)

def est_superutilisateur(user):
    return user.is_authenticated and user.is_superuser

def url_tableau_bord(utilisateur):
    if utilisateur.is_superuser or utilisateur.role == User.Role.ADMINISTRATEUR:
        return "compte:tableau_bord_admin"
    if utilisateur.role == User.Role.EDUCATEUR:
        return "compte:tableau_bord_educateur"
    if utilisateur.role == User.Role.PARENT:
        return "compte:tableau_bord_parent"
    return "compte:connexion"

def accueil(request):
    if request.user.is_authenticated:
        return redirect(url_tableau_bord(request.user))
    return redirect("compte:connexion")

def connexion(request):
    if request.user.is_authenticated:
        return redirect(url_tableau_bord(request.user))

    if request.method == "POST":
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            utilisateur = form.get_user()
            login(request, utilisateur)
            if not form.cleaned_data.get("se_souvenir"):
                request.session.set_expiry(0)
            return redirect(url_tableau_bord(utilisateur))
        elif form.non_field_errors():
            messages.error(request, "Identifiant ou mot de passe incorrect.")
    else:
        form = ConnexionForm(request)

    return render(request, "compte/connexion.html", {"form": form})

@login_required
def tableau_bord_admin(request):
    if not est_administrateur(request.user):
        return redirect(url_tableau_bord(request.user))
    contexte = {
        "titre": "Administrateur",
        "role_page": "admin",
        "nb_educateurs": User.objects.filter(role=User.Role.EDUCATEUR).count(),
        "nb_parents": User.objects.filter(role=User.Role.PARENT).count(),
        "nb_enfants": Enfant.objects.filter(actif=True).count(),
        "nb_groupes": Groupe.objects.count(),
    }
    return render(request, "compte/tableau_bord.html", contexte)

@login_required
def tableau_bord_educateur(request):
    if request.user.role != User.Role.EDUCATEUR:
        return redirect(url_tableau_bord(request.user))

    total_groupes = Groupe.objects.count()
    groupes_pertinents = groupes_pertinents_pour_utilisateur(request.user)

    activites_a_venir = (
        Activite.objects
        .filter(date__gte=timezone.now().date())
        .exclude(lieu__icontains="garderie")  
        .prefetch_related("groupes")
        .annotate(nb_groupes=Count("groupes"))
        .order_by("date")
    )

    activites = [
        activite
        for activite in activites_a_venir
        if activite_visible_par(
            activite, activite.nb_groupes, total_groupes, groupes_pertinents
        )
    ][:12]

    return render(request, "compte/tableau_bord.html", {
        "titre": "Éducateur",
        "role_page": "educateur",   
        "activites": activites,
    })
@login_required
def tableau_bord_parent(request):
    if request.user.role != User.Role.PARENT:
        return redirect(url_tableau_bord(request.user))

    total_groupes = Groupe.objects.count()
    groupes_pertinents = groupes_pertinents_pour_utilisateur(request.user)

    activites_a_venir = (
        Activite.objects
        .filter(date__gte=timezone.now().date())
        .exclude(lieu__icontains="garderie") 
        .prefetch_related("groupes")
        .annotate(nb_groupes=Count("groupes"))
        .order_by("date")
    )

    activites = [
        activite
        for activite in activites_a_venir
        if activite_visible_par(
            activite, activite.nb_groupes, total_groupes, groupes_pertinents
        )
    ][:12]

    return render(request, "compte/tableau_bord.html", {
        "titre": "Parent",
        "role_page": "parent",
        "activites": activites,
    })

# CRUD Administrateur

@login_required
def liste_notifications(request):
    notifications = request.user.notifications.all()

    return render(
        request,
        "compte/liste_notifications.html",
        {"notifications": notifications},
    )

@login_required
def marquer_notification_lue(request, pk):
    notification = get_object_or_404(Notification, pk=pk, destinataire=request.user)

    if request.method == "POST":
        notification.lue = True
        notification.save(update_fields=["lue"])

        if notification.lien:
            return redirect(notification.lien)

    return redirect("compte:liste_notifications")

@login_required
@user_passes_test(est_administrateur)
def creer_administrateur(request):
    if request.method == "POST":
        form = CreationAdministrateurForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(
                request,
                f"Le compte administrateur de {utilisateur.get_full_name() or utilisateur.username} a été créé avec succès."
            )
            return redirect("compte:tableau_bord_admin")
        else:
            messages.error(request, "Impossible de créer le compte administrateur.")
    else:
        form = CreationAdministrateurForm()

    return render(
        request,
        "compte/creer_administrateur.html",
        {"form": form, "titre_page": "Créer un compte administrateur"},
    )

@login_required
def liste_administrateurs(request):
    if not (request.user.is_administrateur or request.user.is_superuser):
        raise PermissionDenied("Vous n'avez pas accès à cette page.")

    recherche = request.GET.get("q", "").strip()

    administrateurs = Administrateur.objects.all().order_by(
        "last_name",
        "first_name"
    )

    if recherche:
        administrateurs = administrateurs.filter(
            Q(first_name__icontains=recherche)
            | Q(last_name__icontains=recherche)
        )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = [
            {
                "id": administrateur.id,
                "nom": administrateur.last_name,
                "prenom": administrateur.first_name,
                "email": administrateur.email,
                "telephone": administrateur.telephone or "",
                "actif": administrateur.is_active,
                "url_detail": reverse(
                    "compte:detail_administrateur",
                    args=[administrateur.id],
                ),
                "url_modifier": reverse(
                    "compte:modifier_administrateur",
                    args=[administrateur.id],
                ),
            }
            for administrateur in administrateurs
        ]

        return JsonResponse({"administrateurs": data})

    return render(
        request,
        "compte/liste_administrateurs.html",
        {
            "administrateurs": administrateurs,
            "recherche": recherche,
        }
    )

@login_required
@user_passes_test(est_administrateur)
def detail_administrateur(request, pk):
    administrateur = get_object_or_404(Administrateur, pk=pk)
    return render(
        request,
        "compte/detail_administrateur.html",
        {"administrateur": administrateur},
    )

@login_required
@user_passes_test(est_administrateur)
def modifier_administrateur(request, pk):
    administrateur = get_object_or_404(Administrateur, pk=pk)

    if request.method == "POST":
        form = ModificationAdministrateurForm(request.POST, instance=administrateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Les informations ont été mises à jour.")
            return redirect("compte:detail_administrateur", pk=administrateur.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ModificationAdministrateurForm(instance=administrateur)

    return render(
        request,
        "compte/modifier_administrateur.html",
        {"form": form, "administrateur": administrateur},
    )

@login_required
@user_passes_test(est_administrateur)
def supprimer_administrateur(request, pk):
    administrateur = get_object_or_404(Administrateur, pk=pk)

    if administrateur.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect("compte:detail_administrateur", pk=pk)

    if request.method == "POST":
        nom = administrateur.get_full_name() or administrateur.username
        administrateur.delete()
        messages.success(request, f"Le compte de {nom} a été supprimé.")
        return redirect("compte:liste_administrateurs")

    return render(
        request,
        "compte/supprimer_administrateur.html",
        {"administrateur": administrateur},
    )

@login_required
@user_passes_test(est_administrateur)
def basculer_statut_administrateur(request, pk):
    administrateur = get_object_or_404(Administrateur, pk=pk)
    if request.method != "POST":
        return redirect("compte:detail_administrateur", pk=pk)
    if administrateur.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect("compte:detail_administrateur", pk=pk)
    administrateur.is_active = not administrateur.is_active
    administrateur.save(update_fields=["is_active"])
    statut = "activé" if administrateur.is_active else "désactivé"
    messages.success(request, f"Le compte de {administrateur} a été {statut}.")
    return redirect("compte:detail_administrateur", pk=pk)

# CRUD Educateur

@login_required
def liste_educateurs(request):
    if not (request.user.is_administrateur or request.user.is_superuser):
        raise PermissionDenied("Vous n'avez pas accès à cette page.")

    recherche = request.GET.get("q", "").strip()

    educateurs = Educateur.objects.all().order_by(
        "last_name",
        "first_name"
    )

    if recherche:
        educateurs = educateurs.filter(
            Q(first_name__icontains=recherche)
            | Q(last_name__icontains=recherche)
        )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = [
            {
                "id": educ.id,
                "nom": educ.last_name,
                "prenom": educ.first_name,
                "email": educ.email,
                "telephone": educ.telephone or "",
                "actif": educ.is_active,
                "url_detail": reverse(
                    "compte:detail_educateur",
                    args=[educ.id],
                ),
                "url_modifier": reverse(
                    "compte:modifier_educateur",
                    args=[educ.id],
                ),
                "url_supprimer": reverse(
                    "compte:supprimer_educateur",
                    args=[educ.id],
                ),
            }
            for educ in educateurs
        ]

        return JsonResponse({"educateurs": data})

    return render(
        request,
        "compte/liste_educateurs.html",
        {
            "educateurs": educateurs,
            "recherche": recherche,
        }
    )

@login_required
@user_passes_test(est_administrateur)
def detail_educateur(request, pk):
    educateur = get_object_or_404(Educateur, pk=pk)
    return render(
        request,
        "compte/detail_educateur.html",
        {"educateur": educateur},
    )

@login_required
@user_passes_test(est_administrateur)
def creer_educateur(request):
    if request.method == "POST":
        form = CreationEducateurForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(
                request,
                f"Le compte educateur de {utilisateur.get_full_name() or utilisateur.username} a été créé avec succès."
            )
            return redirect("compte:liste_educateurs")
        else:
            messages.error(request, "Impossible de créer le compte educateur.")
    else:
        form = CreationEducateurForm()

    return render(
        request,
        "compte/creer_educateur.html",
        {"form": form, "titre_page": "Créer un compte educateur"},
    )

@login_required
@user_passes_test(est_administrateur)
def modifier_educateur(request, pk):
    educateur = get_object_or_404(Educateur, pk=pk)
    if request.method == "POST":
        form = ModificationEducateurForm(request.POST, instance=educateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Les informations ont été mises à jour.")
            return redirect("compte:detail_educateur", pk=educateur.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ModificationEducateurForm(instance=educateur)

    return render(
        request,
        "compte/modifier_educateur.html",
        {"form": form, "educateur": educateur},
    )

@login_required
@user_passes_test(est_administrateur)
def supprimer_educateur(request, pk):
    educateur = get_object_or_404(Educateur, pk=pk)

    if educateur.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect("compte:detail_educateur", pk=pk)

    if request.method == "POST":
        nom = educateur.get_full_name() or educateur.username
        try:
            educateur.delete()
            messages.success(request, f"Le compte de {nom} a été supprimé.")
        except ProtectedError:
            messages.error(
                request,
                f"Impossible de supprimer le compte de {nom} : "
                f"cet éducateur est actuellement assigné à un ou plusieurs groupes. "
                f"Veuillez d'abord lui retirer l'assignation de ses groupes avant de le supprimer."
            )
        return redirect("compte:liste_educateurs")

    return render(
        request,
        "compte/supprimer_educateur.html",
        {"educateur": educateur},
    )

@login_required
@user_passes_test(est_administrateur)
def basculer_statut_educateur(request, pk):
    educateur = get_object_or_404(Educateur, pk=pk)
    if request.method != "POST":
        return redirect("compte:detail_educateur", pk=pk)
    if educateur.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect("compte:detail_educateur", pk=pk)
    educateur.is_active = not educateur.is_active
    educateur.save(update_fields=["is_active"])
    statut = "activé" if educateur.is_active else "désactivé"
    messages.success(request, f"Le compte de {educateur} a été {statut}.")
    return redirect("compte:detail_educateur", pk=pk)

# CRUD Parent

@login_required
def liste_parents(request):
    if not (request.user.is_administrateur or request.user.is_superuser):
        raise PermissionDenied("Vous n'avez pas accès à cette page.")

    recherche = request.GET.get("q", "").strip()

    parents = Parent.objects.all().order_by(
        "last_name",
        "first_name"
    )

    if recherche:
        parents = parents.filter(
            Q(first_name__icontains=recherche)
            | Q(last_name__icontains=recherche)
        )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = [
            {
                "id": parent.id,
                "nom": parent.last_name,
                "prenom": parent.first_name,
                "email": parent.email,
                "telephone": parent.telephone or "",
                "actif": parent.is_active,
                "url_detail": reverse(
                    "compte:detail_parent",
                    args=[parent.id],
                ),
                "url_modifier": reverse(
                    "compte:modifier_parent",
                    args=[parent.id],
                ),
                "url_supprimer": reverse(
                    "compte:supprimer_parent",
                    args=[parent.id],
                ),
            }
            for parent in parents
        ]

        return JsonResponse({"parents": data})

    return render(
        request,
        "compte/liste_parents.html",
        {
            "parents": parents,
            "recherche": recherche,
        }
    )

@login_required
@user_passes_test(est_administrateur)
def detail_parent(request, pk):
    parent = get_object_or_404(Parent, pk=pk)
    return render(
        request,
        "compte/detail_parent.html",
        {"parent": parent},
    )

@login_required
@user_passes_test(est_administrateur)
def creer_parent(request):
    if request.method == "POST":
        form = CreationParentForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(
                request,
                f"Le compte parent de {utilisateur.get_full_name() or utilisateur.username} a été créé avec succès."
            )
            return redirect("compte:liste_parents")
        else:
            messages.error(request, "Impossible de créer le compte parent.")
    else:
        form = CreationParentForm()

    return render(
        request,
        "compte/creer_parent.html",
        {"form": form, "titre_page": "Créer un compte parent"},
    )

@login_required
@user_passes_test(est_administrateur)
def modifier_parent(request, pk):
    parent = get_object_or_404(Parent, pk=pk)

    if request.method == "POST":
        form = ModificationParentForm(request.POST, instance=parent)
        if form.is_valid():
            form.save()
            messages.success(request, "Les informations du parent ont été mises à jour.")
            return redirect("compte:detail_parent", pk=parent.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ModificationParentForm(instance=parent)

    return render(
        request,
        "compte/modifier_parent.html",
        {"form": form, "parent": parent},
    )

@login_required
@user_passes_test(est_administrateur)
def supprimer_parent(request, pk):
    parent = get_object_or_404(Parent, pk=pk)

    if request.method == "POST":
        nom = parent.get_full_name() or parent.username
        try:
            parent.delete()
            messages.success(request, f"Le compte de {nom} a été supprimé.")
        except ProtectedError:
            messages.error(
                request,
                f"Impossible de supprimer le compte de {nom} : "
                f"ce parent a au moins un paiement enregistré. "
                f"Veuillez d'abord traiter ses paiements avant de supprimer son compte."
            )
        return redirect("compte:liste_parents")

    return render(
        request,
        "compte/supprimer_parent.html",
        {"parent": parent},
    )

@login_required
@user_passes_test(est_administrateur)
def basculer_statut_parent(request, pk):
    parent = get_object_or_404(Parent, pk=pk)

    if request.method != "POST":
        return redirect("compte:detail_parent", pk=pk)

    parent.is_active = not parent.is_active
    parent.save(update_fields=["is_active"])

    statut = "activé" if parent.is_active else "désactivé"
    messages.success(request, f"Le compte de {parent} a été {statut}.")
    return redirect("compte:detail_parent", pk=pk)

@login_required
@administrateur_requis
def recherche_rapide_admin(request):
    recherche = request.GET.get("q", "").strip()

    resultats = {
        "educateurs": [],
        "parents": [],
        "groupes": [],
        "enfants": [],
        "activites": [],
    }

    if recherche:
        educateurs = (
            Educateur.objects
            .filter(
                Q(first_name__icontains=recherche)
                | Q(last_name__icontains=recherche)
            )
            .order_by("last_name", "first_name")[:5]
        )

        parents = (
            Parent.objects
            .filter(
                Q(first_name__icontains=recherche)
                | Q(last_name__icontains=recherche)
            )
            .order_by("last_name", "first_name")[:5]
        )

        groupes = (
            Groupe.objects
            .filter(
                nom__icontains=recherche
            )
            .order_by("nom")[:5]
        )

        enfants = (
            Enfant.objects
            .filter(
                Q(prenom__icontains=recherche)
                | Q(nom__icontains=recherche)
            )
            .order_by("nom", "prenom")[:5]
        )

        activites = (
            Activite.objects
            .filter(
                nom__icontains=recherche
            )
            .order_by("date")[:5]
        )

        resultats["educateurs"] = [
            {
                "id": educateur.id,
                "nom": f"{educateur.first_name} {educateur.last_name}",
                "url": reverse(
                    "compte:detail_educateur",
                    args=[educateur.id],
                ),
            }
            for educateur in educateurs
        ]

        resultats["parents"] = [
            {
                "id": parent.id,
                "nom": f"{parent.first_name} {parent.last_name}",
                "url": reverse(
                    "compte:detail_parent",
                    args=[parent.id],
                ),
            }
            for parent in parents
        ]

        resultats["groupes"] = [
            {
                "id": groupe.id,
                "nom": groupe.nom,
                "url": reverse(
                    "detail_groupe",
                    args=[groupe.id],
                ),
            }
            for groupe in groupes
        ]

        resultats["enfants"] = [
            {
                "id": enfant.id,
                "nom": f"{enfant.prenom} {enfant.nom}",
                "url": reverse(
                    "fiche_enfant",
                    args=[enfant.id],
                ),
            }
            for enfant in enfants
        ]

        resultats["activites"] = [
            {
                "id": activite.id,
                "nom": activite.nom,
                "url": reverse(
                    "detail_activite",
                    args=[activite.id],
                ),
            }
            for activite in activites
        ]

    return JsonResponse(resultats)