from PIL import Image

from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator, MinValueValidator
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
            "L'image ne doit pas dépasser %(max)s Mo (taille actuelle : %(actuelle)s Mo)." % {
                "max": TAILLE_MAX_PHOTO // (1024 * 1024),
                "actuelle": round(fichier.size / (1024 * 1024), 1),
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

    def clean(self):
        super().clean()

        if self.date and self.date < timezone.now().date():
            # On ne bloque que si la date est en train d'être fixée ou
            # changée vers une date passée : sinon, une activité déjà
            # passée deviendrait impossible à modifier (ex. corriger une
            # faute dans la description), même sans toucher à la date.
            date_modifiee = self._state.adding or (
                Activite.objects.filter(pk=self.pk)
                .exclude(date=self.date)
                .exists()
            )
            if date_modifiee:
                raise ValidationError({
                    "date":
                        "La date de l'activité ne peut pas être dans le passé."
                })

    @property
    def photo_url(self):
        """URL de la photo de l'activité, ou une photo par défaut si l'admin n'en a pas fourni."""
        if self.photo:
            return self.photo.url

        return static("enfants/img/activite_defaut.jpg")

    @property
    def frais_affichage(self):
        """Affichage des frais d'inscription : "Gratuit" si 0 $, sinon le montant."""
        if self.frais_inscription == 0:
            return "Gratuit"

        return f"{self.frais_inscription} $"

    @property
    def applique_a_tous_les_groupes(self):
        """
        True si l'activité ne cible aucun groupe en particulier : soit aucun groupe
        n'a été sélectionné, soit l'admin a sélectionné tous les groupes existants
        un par un, ce qui revient au même.

        Pratique pour une seule activité (ex. page de détail), mais à éviter dans une
        boucle sur une liste d'activités : chaque appel fait une requête sur Groupe en
        plus de celle sur self.groupes. Pour une liste, annoter le queryset avec
        Count("groupes") et comparer au nombre total de groupes (voir liste_activites)
        plutôt que d'utiliser cette propriété.
        """
        groupes_selectionnes = {groupe.pk for groupe in self.groupes.all()}

        if not groupes_selectionnes:
            return True

        tous_les_groupes = set(Groupe.objects.values_list("pk", flat=True))

        return groupes_selectionnes == tous_les_groupes

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.photo:
            self._redimensionner_photo()

    def _redimensionner_photo(self):
        """
        Réduit la photo si ses dimensions dépassent DIMENSION_MAX_PHOTO, pour éviter
        qu'une image aux dimensions excessives (ex. photo prise directement par un
        appareil photo, plusieurs milliers de pixels de large) casse l'affichage
        (carrousel, cartes) ou gonfle inutilement le poids servi aux parents/éducateurs.
        Ne fait rien si la photo est déjà dans les limites (pas d'agrandissement).
        """
        chemin = self.photo.path

        with Image.open(chemin) as image:
            if image.width <= DIMENSION_MAX_PHOTO and image.height <= DIMENSION_MAX_PHOTO:
                return

            image = image.convert("RGB") if image.mode not in ("RGB", "L") else image
            image.thumbnail((DIMENSION_MAX_PHOTO, DIMENSION_MAX_PHOTO))
            image.save(chemin)

    def __str__(self):
        return str(self.nom)
