from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

valider_telephone = RegexValidator(
    regex=r"^(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",
    message=(
        "Numéro de téléphone invalide."
    ),
)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMINISTRATEUR = "administrateur", "Administrateur"
        EDUCATEUR = "educateur(trice)", "Éducateur(trice)"
        PARENT = "parent", "Parent"

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        verbose_name="Rôle",
        help_text="Détermine l'espace personnel et les droits d'accès de l'utilisateur.",
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone",
        validators=[valider_telephone],
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_administrateur(self):
        return self.role == self.Role.ADMINISTRATEUR

    @property
    def is_educateur(self):
        return self.role == self.Role.EDUCATEUR

    @property
    def is_parent(self):
        return self.role == self.Role.PARENT


class Administrateur(User):
    class Meta:
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"


class Educateur(User):
    class Meta:
        verbose_name = "Éducateur(trice)"
        verbose_name_plural = "Éducateurs(trices)"


class Parent(User):
    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
