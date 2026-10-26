from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class CourrielOuNomUtilisateurBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            utilisateur = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            # On "vérifie" quand même un mot de passe factice, pour que le
            # temps de réponse soit similaire que l'utilisateur existe ou
            # non (évite de pouvoir deviner si un email/nom existe via le
            # délai de réponse). C'est exactement ce que fait ModelBackend.
            User().set_password(password)
            return None
        if utilisateur.check_password(password) and self.user_can_authenticate(utilisateur):
            return utilisateur
        return None
