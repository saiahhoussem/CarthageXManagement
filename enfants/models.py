from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


telephone_validator = RegexValidator(
    regex=r"^[0-9]{3}[-. ]?[0-9]{3}[-. ]?[0-9]{4}$",
    message="Le numéro de téléphone doit contenir 10 chiffres."
)


class Groupe(models.Model):
    nom = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(
                3,
                "Le nom du groupe doit contenir au moins 3 caractères."
            )
        ]
    )

    educateur = models.ForeignKey(
    "compte.Educateur",
    on_delete=models.PROTECT,
    related_name="groupes",
    null=True,
    blank=True
    )
    def __str__(self):
        return self.nom

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
    date_naissance = models.DateField(
    )
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