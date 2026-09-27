from django.contrib.auth.models import AbstractUser
from django.db import models


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
