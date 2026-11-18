from PIL import Image

from django.db import models
from django.core.validators import (
    MinLengthValidator,
    RegexValidator,
    MinValueValidator,
)
from django.core.exceptions import ValidationError
from django.templatetags.static import static
from django.utils import timezone


telephone_validator = RegexValidator(
    regex=r"^[0-9]{3}[-. ]?[0-9]{3}[-. ]?[0-9]{4}$",
    message="Le numéro de téléphone doit contenir 10 chiffres."
)

TAILLE_MAX_PHOTO = 5 * 1024 * 1024  # 5 Mo
DIMENSION_MAX_PHOTO = 1600  # pixels, largeur et hauteur


def valider_taille_photo(fichier):
    if fichier.size > TAILLE_MAX_PHOTO:
        raise ValidationError(
            "L'image ne doit pas dépasser %(max)s Mo "
            "(taille actuelle : %(actuelle)s Mo)." % {
                "max": TAILLE_MAX_PHOTO // (1024 * 1024),
                "actuelle": round(
                    fichier.size / (1024 * 1024),
                    1
                ),
            }
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

    @property
    def places_restantes(self):
        return max(
            self.capacite - self.enfant_set.count(),
            0
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

    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.PROTECT
    )

    date_naissance = models.DateField()

    parents = models.ManyToManyField(
        "compte.Parent",
        related_name="enfants",
        blank=True
    )

    actif = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )

    def clean(self):
        super().clean()

        if (
            self.date_naissance
            and self.date_naissance >= timezone.now().date()
        ):
            raise ValidationError({
                "date_naissance":
                    "La date de naissance doit être dans le passé."
            })

        if (
            self.groupe_id
            and self.groupe.educateur_id is None
        ):
            raise ValidationError({
                "groupe":
                    "Ce groupe n'a pas encore d'éducateur assigné "
                    "et ne peut donc pas accueillir d'enfants."
            })

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Allergie(models.Model):
    enfant = models.ForeignKey(
        Enfant,
        on_delete=models.CASCADE
    )

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
    enfant = models.ForeignKey(
        Enfant,
        on_delete=models.CASCADE
    )

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
                "Le nom doit contenir au moins 3 caractères."
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

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    date_modification = models.DateTimeField(
        auto_now=True
    )

    def clean(self):
        super().clean()

        if (
            self.date_naissance
            and self.date_naissance >= timezone.now().date()
        ):
            raise ValidationError({
                "date_naissance":
                    "La date de naissance doit être dans le passé."
            })

    def __str__(self):
        return (
            f"{self.prenom_enfant} "
            f"{self.nom_enfant} "
            f"({self.get_statut_display()})"
        )


class PersonneAutorisee(models.Model):
    enfant = models.ForeignKey(
        Enfant,
        on_delete=models.CASCADE
    )

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

    places_disponibles = models.PositiveIntegerField(
        default=20,
        verbose_name="Nombre de places disponibles",
        validators=[
            MinValueValidator(
                1,
                "Le nombre de places disponibles doit être d'au moins 1."
            )
        ]
    )

    groupes = models.ManyToManyField(
        Groupe,
        related_name="activites",
        blank=True,
    )

    description = models.TextField(
        validators=[
            MinLengthValidator(
                2,
                "La description doit contenir au moins 2 caractères."
            )
        ]
    )

    photo = models.ImageField(
        upload_to="activites/",
        blank=True,
        null=True,
        validators=[valider_taille_photo],
    )

    heure_debut = models.TimeField(
        verbose_name="Heure de début",
        help_text="Heure de début de l'activité (pour l'horaire des éducateurs).",
    )
    heure_fin = models.TimeField(
        verbose_name="Heure de fin",
        help_text="Heure de fin de l'activité.",
    )
    annulee = models.BooleanField(default=False, verbose_name="Annulée")

    def clean(self):
        super().clean()

        if self.date and self.date < timezone.now().date():
            # On ne bloque que si la date est en train d'être fixée
            # ou changée vers une date passée.
            date_modifiee = (
                self._state.adding
                or Activite.objects.filter(
                    pk=self.pk
                ).exclude(
                    date=self.date
                ).exists()
            )

            if date_modifiee:
                raise ValidationError({
                    "date":
                        "La date de l'activité ne peut pas être "
                        "dans le passé."
                })

    @property
    def plage_horaire(self):
        """Retourne 'HH:MM – HH:MM' ou 'Horaire à préciser'."""
        if self.heure_debut and self.heure_fin:
            return f"{self.heure_debut:%H:%M} – {self.heure_fin:%H:%M}"
        return "Horaire à préciser"

    @property
    def places_restantes(self):
        nb_inscriptions = getattr(self, "nb_inscriptions", None)

        if nb_inscriptions is None:
            nb_inscriptions = self.inscriptions.count()

        return max(self.places_disponibles - nb_inscriptions, 0)

    @property
    def photo_url(self):
        """
        URL de la photo de l'activité, ou une photo par défaut
        si l'admin n'en a pas fourni.
        """
        if self.photo:
            return self.photo.url

        return static(
            "enfants/img/activite_defaut.jpg"
        )

    @property
    def frais_affichage(self):
        """
        Affichage des frais d'inscription :
        "Gratuit" si 0 $, sinon le montant.
        """
        if self.frais_inscription == 0:
            return "Gratuit"

        return f"{self.frais_inscription} $"

    @property
    def applique_a_tous_les_groupes(self):
        """
        True si l'activité ne cible aucun groupe en particulier :
        soit aucun groupe n'a été sélectionné,
        soit l'admin a sélectionné tous les groupes existants.
        """
        groupes_selectionnes = {
            groupe.pk
            for groupe in self.groupes.all()
        }

        if not groupes_selectionnes:
            return True

        tous_les_groupes = set(
            Groupe.objects.values_list(
                "pk",
                flat=True
            )
        )

        return (
            groupes_selectionnes
            == tous_les_groupes
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.photo:
            self._redimensionner_photo()

    def _redimensionner_photo(self):
        """
        Réduit la photo si ses dimensions dépassent
        DIMENSION_MAX_PHOTO.
        """
        chemin = self.photo.path

        with Image.open(chemin) as image:
            if (
                image.width <= DIMENSION_MAX_PHOTO
                and image.height <= DIMENSION_MAX_PHOTO
            ):
                return

            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            image.thumbnail(
                (
                    DIMENSION_MAX_PHOTO,
                    DIMENSION_MAX_PHOTO
                )
            )

            image.save(chemin)

    def __str__(self):
        return str(self.nom)


class InscriptionActivite(models.Model):
    activite = models.ForeignKey(
        Activite,
        on_delete=models.CASCADE,
        related_name="inscriptions",
    )
    enfant = models.ForeignKey(
        Enfant,
        on_delete=models.CASCADE,
        related_name="inscriptions_activites",
    )
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["activite", "enfant"],
                name="unique_inscription_activite_enfant",
            )
        ]
        ordering = ["-date_inscription"]

    def __str__(self):
        return f"{self.enfant} - {self.activite}"


def groupes_pertinents_pour_utilisateur(utilisateur):
    """
    Ensemble des ids de Groupe concernant cet utilisateur :
    groupe de l'éducateur ou groupes des enfants d'un parent.
    """
    if utilisateur.is_educateur:
        return set(
            Groupe.objects.filter(
                educateur__pk=utilisateur.pk
            ).values_list(
                "pk",
                flat=True
            )
        )

    if utilisateur.is_parent:
        return set(
            Enfant.objects.filter(
                parents__pk=utilisateur.pk
            ).values_list(
                "groupe_id",
                flat=True
            )
        )

    return set()


def activite_visible_par(
    activite,
    nb_groupes,
    total_groupes,
    groupes_pertinents
):
    """
    Détermine si une activité doit être visible
    pour un utilisateur.
    """
    if (
        nb_groupes == 0
        or nb_groupes == total_groupes
    ):
        return True

    ids_groupes_activite = {
        groupe.pk
        for groupe in activite.groupes.all()
    }

    return bool(
        ids_groupes_activite
        & groupes_pertinents
    )


class Presence(models.Model):
    class Type(models.TextChoices):
        ABSENCE = "absence", "Absence"
        RETARD = "retard", "Retard"

    class SourceSignalement(models.TextChoices):
        PARENT = "parent", "Parent"
        EDUCATEUR = "educateur", "Éducateur(trice)"
        ADMINISTRATEUR = "administrateur", "Administrateur"

    enfant = models.ForeignKey(
        Enfant,
        on_delete=models.CASCADE,
        related_name="presences"
    )

    type = models.CharField(
        max_length=20,
        choices=Type.choices
    )

    date = models.DateField()

    date_fin = models.DateField(
        null=True,
        blank=True
    )

    heure = models.TimeField()

    heure_fin = models.TimeField(
        null=True,
        blank=True
    )

    motif = models.TextField(
        max_length=500
    )

    source_signalement = models.CharField(
        max_length=20,
        choices=SourceSignalement.choices
    )

    parent = models.ForeignKey(
        "compte.Parent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signalements_presence"
    )

    educateur = models.ForeignKey(
        "compte.Educateur",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signalements_presence"
    )

    date_signalement = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "enfant",
                    "date",
                    "type"
                ],
                name="unique_presence_enfant_date_type"
            )
        ]

    def clean(self):
        super().clean()

        # Pour un retard, la date de fin correspond
        # automatiquement à la date de début.
        if (
            self.type == self.Type.RETARD
            and self.date
        ):
            self.date_fin = self.date

        # Pour une absence, la date de fin ne peut pas
        # être antérieure à la date de début.
        if (
            self.type == self.Type.ABSENCE
            and self.date
            and self.date_fin
            and self.date_fin < self.date
        ):
            raise ValidationError({
                "date_fin": (
                    "La date de fin doit être égale "
                    "ou postérieure à la date de début."
                )
            })

        # Pour un retard, l'heure de fin est obligatoire
        # et doit être postérieure à l'heure de début.
        if self.type == self.Type.RETARD:

            if not self.heure_fin:
                raise ValidationError({
                    "heure_fin": (
                        "L'heure de fin est obligatoire "
                        "pour un retard."
                    )
                })

            if (
                self.heure
                and self.heure_fin
                and self.heure_fin <= self.heure
            ):
                raise ValidationError({
                    "heure_fin": (
                        "L'heure de fin doit être postérieure "
                        "à l'heure de début."
                    )
                })

        # Pour une absence, heure_fin n'est pas utilisée.
        if self.type == self.Type.ABSENCE:
            self.heure_fin = None

        # Vérification des chevauchements
        # uniquement pour les absences.
        if (
            self.enfant_id
            and self.type == self.Type.ABSENCE
            and self.date
        ):
            nouvelle_date_fin = (
                self.date_fin
                or self.date
            )

            absences_existantes = (
                Presence.objects
                .filter(
                    enfant_id=self.enfant_id,
                    type=self.Type.ABSENCE,
                    date__lte=nouvelle_date_fin
                )
                .filter(
                    models.Q(
                        date_fin__gte=self.date
                    )
                    | models.Q(
                        date_fin__isnull=True,
                        date__gte=self.date
                    )
                )
            )

            # En modification, on ignore
            # la présence elle-même.
            if self.pk:
                absences_existantes = (
                    absences_existantes.exclude(
                        pk=self.pk
                    )
                )

            if absences_existantes.exists():
                raise ValidationError({
                    "date": (
                        "Une absence existe déjà pour cet enfant "
                        "pendant cette période."
                    )
                })

    def save(self, *args, **kwargs):
        # Un retard doit toujours avoir
        # date_fin = date.
        if (
            self.type == self.Type.RETARD
            and self.date
        ):
            self.date_fin = self.date

        # Une absence ne doit pas conserver
        # d'heure de fin.
        if self.type == self.Type.ABSENCE:
            self.heure_fin = None

        super().save(*args, **kwargs)

    @property
    def date_fin_effective(self):
        """
        Retourne la date de fin réelle du signalement.

        Pour une absence d'une seule journée,
        date_fin est vide, donc on utilise date.
        """
        return self.date_fin or self.date

    def __str__(self):
        return (
            f"{self.enfant} - "
            f"{self.get_type_display()} - "
            f"{self.date} {self.heure}"
        )