from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from .forms import CreationCompteForm
from .models import User


def est_administrateur(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == User.Role.ADMINISTRATEUR
    )


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
            return redirect("utilisateurs:creer_compte")
        else:
            messages.error(request, "L'utilisateur n'a pas été ajouté à la liste.")
    else:
        form = CreationCompteForm()

    return render(request, "utilisateurs/creer_compte.html", {"form": form})
