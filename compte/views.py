from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import redirect, render, get_object_or_404
from .models import Educateur, User, Parent
from .forms import ( 
    ConnexionForm, 
    CreationAdministrateurForm, 
    CreationEducateurForm, 
    ModificationEducateurForm,
    CreationParentForm, 
    ModificationParentForm
)
from django.utils import timezone

from enfants.models import (
    Activite,
    Enfant,
    Groupe,
    groupes_pertinents_pour_utilisateur,
    activite_visible_par,
)

def est_administrateur(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == User.Role.ADMINISTRATEUR
    )

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

ROLES_CREATION = {
    "educateur": User.Role.EDUCATEUR,
    "parent": User.Role.PARENT,
}

TITRES_CREATION = {
    User.Role.EDUCATEUR: "Créer un compte éducateur",
    User.Role.PARENT: "Créer un compte parent",
}

@login_required
def tableau_bord_admin(request):
    if not est_administrateur(request.user):
        return redirect(url_tableau_bord(request.user))
    contexte = {
        "titre": "Administrateur",
        "nb_educateurs": User.objects.filter(role=User.Role.EDUCATEUR).count(),
        "nb_parents": User.objects.filter(role=User.Role.PARENT).count(),
        "nb_enfants": Enfant.objects.count(),
        "nb_groupes": Groupe.objects.count(),
    }
    return render(request, "compte/tableau_bord.html", contexte)

@login_required
def tableau_bord_educateur(request):
    if request.user.role != User.Role.EDUCATEUR:
        return redirect(url_tableau_bord(request.user))
    return render(request, "compte/tableau_bord.html", {"titre": "Éducateur"})

@login_required
def tableau_bord_parent(request):
    if request.user.role != User.Role.PARENT:
        return redirect(url_tableau_bord(request.user))

    total_groupes = Groupe.objects.count()
    groupes_pertinents = groupes_pertinents_pour_utilisateur(request.user)

    activites_a_venir = (
        Activite.objects
        .filter(date__gte=timezone.now().date())
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
        "activites": activites,
    })

# CRUD Administrateur

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

# CRUD Educateur

@login_required
@user_passes_test(est_administrateur)
def liste_educateurs(request):
    educateurs = Educateur.objects.all().order_by("last_name", "first_name")
    return render(
        request,
        "compte/liste_educateurs.html",
        {"educateurs": educateurs},
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
@user_passes_test(est_administrateur)
def liste_parents(request):
    parents = Parent.objects.all().order_by("last_name", "first_name")
    return render(
        request,
        "compte/liste_parents.html",
        {"parents": parents},
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
def basculer_statut_parent(request, pk):
    parent = get_object_or_404(Parent, pk=pk)

    if request.method != "POST":
        return redirect("compte:detail_parent", pk=pk)

    parent.is_active = not parent.is_active
    parent.save(update_fields=["is_active"])

    statut = "activé" if parent.is_active else "désactivé"
    messages.success(request, f"Le compte de {parent} a été {statut}.")
    return redirect("compte:detail_parent", pk=pk)
