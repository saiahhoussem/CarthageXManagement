def notifications(request):
    if not request.user.is_authenticated:
        return {"nb_notifications_non_lues": 0}

    return {
        "nb_notifications_non_lues": request.user.notifications.filter(lue=False).count()
    }
