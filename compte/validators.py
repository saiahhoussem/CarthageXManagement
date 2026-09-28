from django.contrib.auth.password_validation import (
    CommonPasswordValidator,
    MinimumLengthValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator,
)
from django.core.exceptions import ValidationError


class ValidateurLongueurMinimale(MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                f"Le mot de passe doit contenir au moins {self.min_length} caractères.",
                code="password_too_short",
            )

    def get_help_text(self):
        return f"Le mot de passe doit contenir au moins {self.min_length} caractères."


class ValidateurSimilariteUtilisateur(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Ce mot de passe ressemble trop à vos informations personnelles "
                "(nom d'utilisateur, prénom, nom ou courriel).",
                code="password_too_similar",
            )

    def get_help_text(self):
        return "Le mot de passe ne doit pas trop ressembler à vos autres informations personnelles."


class ValidateurMotDePasseCourant(CommonPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Ce mot de passe est trop courant et facile à deviner.",
                code="password_too_common",
            )

    def get_help_text(self):
        return "Le mot de passe ne peut pas être un mot de passe couramment utilisé."


class ValidateurMotDePasseNumerique(NumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Ce mot de passe ne peut pas être composé uniquement de chiffres.",
                code="password_entirely_numeric",
            )

    def get_help_text(self):
        return "Le mot de passe ne peut pas être entièrement numérique."
