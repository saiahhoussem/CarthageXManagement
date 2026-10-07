from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404

from .forms import ConnexionForm, CreationCompteForm, ModificationEducateurForm
from .models import Educateur, User, Parent


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
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
    else:
        form = ConnexionForm(request)

    return render(request, "compte/connexion.html", {"form": form})


@login_required
@user_passes_test(est_administrateur)
def creer_compte(request):
    if request.method == "POST":
        form = CreationCompteForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(
                request,
                f"Le compte de {utilisateur.get_full_name() or utilisateur.username} "
                f"a été créé avec succès.",
            )
            return redirect("compte:creer_compte")
        else:
            messages.error(request, "Impossible de créer le compte.")
    else:
        form = CreationCompteForm()

    return render(request, "compte/creer_compte.html", {"form": form})


@login_required
def tableau_bord_admin(request):
    if not est_administrateur(request.user):
        return redirect(url_tableau_bord(request.user))
    return render(request, "compte/tableau_bord.html", {"titre": "Administrateur"})


@login_required
def tableau_bord_educateur(request):
    if request.user.role != User.Role.EDUCATEUR:
        return redirect(url_tableau_bord(request.user))
    return render(request, "compte/tableau_bord.html", {"titre": "Éducateur(trice)"})


@login_required
def tableau_bord_parent(request):
    if request.user.role != User.Role.PARENT:
        return redirect(url_tableau_bord(request.user))
    return render(request, "compte/tableau_bord.html", {"titre": "Parent"})


@login_required
@user_passes_test(est_administrateur)
def liste_educateurs(request):
    """Liste toutes les éducatrices (actives et inactives)."""
    educateurs = Educateur.objects.all().order_by("last_name", "first_name")
    return render(
        request,
        "compte/liste_educateurs.html",
        {"educateurs": educateurs},
    )


@login_required
@user_passes_test(est_administrateur)
def detail_educateur(request, pk):
    """Détail d'une éducatrice."""
    educateur = get_object_or_404(Educateur, pk=pk)
    return render(
        request,
        "compte/detail_educateur.html",
        {"educateur": educateur},
    )


@login_required
@user_passes_test(est_administrateur)
def modifier_educateur(request, pk):
    """Modification des informations d'une éducatrice."""
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
    """Désactive ou réactive le compte d'une éducatrice (POST uniquement)."""
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

@login_required
@user_passes_test(est_administrateur)
def liste_parents(request):
    """Liste toutes les parents."""
    parents = Parent.objects.all().order_by("last_name", "first_name")
    return render(
        request,
        "compte/liste_parents.html",
        {"parents": parents},
    )