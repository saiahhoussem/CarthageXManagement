from functools import wraps

from django.core.exceptions import PermissionDenied


def _acces_reserve(condition, message="Vous n'avez pas accès à cette page."):
    """
    Construit un décorateur de vue qui lève PermissionDenied(message) si
    `condition(request.user)` est faux.

    À utiliser uniquement pour des vérifications de rôle pur, qui ne
    dépendent d'aucun objet précis (groupe, enfant, demande...). Pour une
    vérification qui dépend d'un objet (ex. "ce parent peut-il accéder à
    CET enfant précis"), garder la vérification inline dans la vue —
    voir `utilisateur_peut_acceder_enfant` plus bas dans ce fichier
    (enfants/views.py).

    S'utilise toujours APRÈS @login_required (donc juste en-dessous),
    puisque la condition suppose que request.user est authentifié.
    """
    def decorateur(vue):
        @wraps(vue)
        def vue_protegee(request, *args, **kwargs):
            if not condition(request.user):
                raise PermissionDenied(message)
            return vue(request, *args, **kwargs)
        return vue_protegee
    return decorateur


# Réservé aux administrateurs (et superutilisateurs).
administrateur_requis = _acces_reserve(
    lambda user: user.is_administrateur or user.is_superuser
)

# Réservé aux parents.
parent_requis = _acces_reserve(lambda user: user.is_parent)

# Réservé aux éducateurs(trices).
educateur_requis = _acces_reserve(lambda user: user.is_educateur)

# Réservé aux éducateurs(trices) et aux parents.
educateur_ou_parent_requis = _acces_reserve(
    lambda user: user.is_educateur or user.is_parent
)
