from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


telephone_validator = RegexValidator(
    regex=r"^[0-9]{3}[-. ]?[0-9]{3}[-. ]?[0-9]{4}$",
    message="Le numéro de téléphone doit contenir 10 chiffres."
)

class Groupe(models.Model):
    class TrancheAge(models.TextChoices):
        BEBE = "0-18", "0 à 18 mois"
        TROTTEUR = "18-36", "18 à 36 mois"
        PRESCOLAIRE = "36-60", "3 à 5 ans"

    nom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                3,
                "Le nom du groupe doit contenir au moins 3 caractères."
            )
        ]
    )

    tranche_age = models.CharField(
        max_length=20,
        choices=TrancheAge.choices
    )

    capacite = models.PositiveIntegerField(
        default=10,
        verbose_name="Capacité maximale",
        validators=[
            MinValueValidator(
                1,
                "La capacité du groupe doit être d'au moins 1 enfant."
            )
        ]
    )

    educateur = models.OneToOneField(
        "compte.Educateur",
        on_delete=models.PROTECT,
        related_name="groupe",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.nom)


class Enfant(models.Model):
    prenom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                2,
                "Le prénom doit contenir au moins 2 caractères."
            )
        ]
    )
    nom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                3,
                "Le nom de l'enfant doit contenir au moins 3 caractères."
            )
        ]
    )
    groupe = models.ForeignKey(Groupe, on_delete=models.PROTECT)
    date_naissance = models.DateField()
    parents = models.ManyToManyField(
        "compte.Parent",
        related_name="enfants",
        blank=True
    )

    def clean(self):
        super().clean()

        if self.date_naissance and self.date_naissance >= timezone.now().date():
            raise ValidationError({
                "date_naissance":
                    "La date de naissance doit être dans le passé."
            })

        if self.groupe_id and self.groupe.educateur_id is None:
            raise ValidationError({
                "groupe":
                    "Ce groupe n'a pas encore d'éducateur assigné et ne "
                    "peut donc pas accueillir d'enfants."
            })

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Allergie(models.Model):
    enfant = models.ForeignKey(Enfant, on_delete=models.CASCADE)

    type_allergie = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                2,
                "Le type d'allergie doit contenir au moins 2 caractères."
            )
        ]
    )

    reaction = models.TextField(
        max_length=500,
        validators=[
            MinLengthValidator(
                2,
                "La réaction doit contenir au moins 2 caractères."
            )
        ]
    )

    def __str__(self):
        return self.type_allergie


class ContactUrgence(models.Model):
    enfant = models.ForeignKey(Enfant, on_delete=models.CASCADE)

    prenom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                2,
                "Le prénom doit contenir au moins 2 caractères."
            )
        ]
    )

    nom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                3,
                "Le nom doit contenir au moins 3 caractères."
            )
        ]
    )

    telephone = models.CharField(
        max_length=12,
        validators=[telephone_validator]
    )

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class DemandeInscription(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        APPROUVEE = "approuvee", "Approuvée"
        REFUSEE = "refusee", "Refusée"

    parent = models.ForeignKey(
        "compte.Parent",
        on_delete=models.CASCADE,
        related_name="demandes_inscription"
    )

    prenom_enfant = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                2,
                "Le prénom doit contenir au moins 2 caractères."
            )
        ]
    )
    nom_enfant = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                3,
                "Le nom de l'enfant doit contenir au moins 3 caractères."
            )
        ]
    )
    date_naissance = models.DateField()

    note = models.TextField(
        max_length=500,
        blank=True
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        if self.date_naissance and self.date_naissance >= timezone.now().date():
            raise ValidationError({
                "date_naissance":
                    "La date de naissance doit être dans le passé."
            })

    def __str__(self):
        return f"{self.prenom_enfant} {self.nom_enfant} ({self.get_statut_display()})"


class PersonneAutorisee(models.Model):
    enfant = models.ForeignKey(Enfant, on_delete=models.CASCADE)

    prenom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                2,
                "Le prénom doit contenir au moins 2 caractères."
            )
        ]
    )
    nom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                3,
                "Le nom doit contenir au moins 3 caractères."
            )
        ]
    )

    relation = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                2,
                "La relation doit contenir au moins 2 caractères."
            )
        ]
    )

    telephone = models.CharField(
        max_length=12,
        validators=[telephone_validator]
    )

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Activite(models.Model):
    nom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                3,
                "Le nom de l'activité doit contenir au moins 3 caractères."
            )
        ]
    )

    date = models.DateField()

    lieu = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(
                2,
                "Le lieu doit contenir au moins 2 caractères."
            )
        ]
    )

    frais_inscription = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(
                0,
                "Les frais d'inscription ne peuvent pas être négatifs."
            )
        ]
    )

    groupes = models.ManyToManyField(
        Groupe,
        related_name="activites",
        blank=True,
    )

    def __str__(self):
        return str(self.nom)
