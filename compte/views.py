from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from .forms import ConnexionForm, CreationCompteForm
from .models import User


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
            messages.error(request, "L'utilisateur n'a pas été ajouté à la liste.")
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
