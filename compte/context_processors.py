def notifications(request):
    if not request.user.is_authenticated:
        return {"nb_notifications_non_lues": 0}

    return {
        "nb_notifications_non_lues": request.user.notifications.filter(lue=False).count()
    }

def educateur_groupe(request):
    """
    Expose educateur_groupe_id à tous les templates.

    Retourne {} si l'utilisateur n'est pas un éducateur connecté.
    """
    if not request.user.is_authenticated:
        return {}

    if not request.user.is_educateur:
        return {}

    from enfants.models import Groupe

    groupe = (
        Groupe.objects
        .filter(educateur=request.user)
        .only("id")
        .first()
    )

    return {
        "educateur_groupe_id": groupe.id if groupe else None,
    }
