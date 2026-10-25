from django import forms
from django.db.models import Count, F

from .models import Activite, Allergie, ContactUrgence, Groupe, PersonneAutorisee, DemandeInscription
from compte.models import Educateur


class AllergieForm(forms.ModelForm):
    class Meta:
        model = Allergie
        fields = ["type_allergie", "reaction"]

        error_messages = {
            "type_allergie": {
                "required": "Le type de l'allergie est obligatoire."
            },
            "reaction": {
                "required": "Veuillez préciser la réaction provoquée par cette allergie."
            }
        }

        widgets = {
            "reaction": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Décrivez la réaction provoquée par l'allergie."
                }
            )
        }


class DemandeInscriptionForm(forms.ModelForm):
    class Meta:
        model = DemandeInscription
        fields = ["prenom_enfant", "nom_enfant", "date_naissance", "note"]

        labels = {
            "prenom_enfant": "Prénom de l'enfant",
            "nom_enfant": "Nom de l'enfant",
            "date_naissance": "Date de naissance",
            "note": "Note (optionnelle)",
        }

        widgets = {
            "prenom_enfant": forms.TextInput(attrs={
                "placeholder": "Prénom de l'enfant"
            }),
            "nom_enfant": forms.TextInput(attrs={
                "placeholder": "Nom de l'enfant"
            }),
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Informations complémentaires pour l'administration (optionnel)."
            })
        }

        error_messages = {
            "prenom_enfant": {"required": "Veuillez indiquer le prénom de l'enfant."},
            "nom_enfant": {"required": "Veuillez indiquer le nom de l'enfant."},
            "date_naissance": {"required": "Veuillez indiquer la date de naissance de l'enfant."}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ContactUrgenceForm(forms.ModelForm):
    class Meta:
        model = ContactUrgence
        fields = ["prenom", "nom", "telephone"]

        error_messages = {
            "prenom": {
                "required": "Veuillez indiquer le prénom du contact d'urgence."
            },
            "nom": {
                "required": "Veuillez indiquer le nom du contact d'urgence."
            },
            "telephone": {
                "required": "Veuillez indiquer un numéro de téléphone pour joindre cette personne."
            }
        }

        widgets = {
            "telephone": forms.TextInput(
                attrs={
                    "placeholder": "418-555-1234",
                    "maxlength": "12"
                }
            )
        }


class PersonneAutoriseeForm(forms.ModelForm):
    class Meta:
        model = PersonneAutorisee
        fields = ["prenom", "nom", "relation", "telephone"]

        error_messages = {
            "prenom": {
                "required": "Veuillez indiquer le prénom de la personne autorisée."
            },
            "nom": {
                "required": "Veuillez indiquer le nom de la personne autorisée."
            },
            "relation": {
                "required": "Veuillez préciser le lien entre l'enfant et la personne autorisée."
            },
            "telephone": {
                "required": "Veuillez indiquer un numéro de téléphone pour joindre cette personne."
            }
        }

        widgets = {
            "telephone": forms.TextInput(
                attrs={
                    "placeholder": "418-555-1234",
                    "maxlength": "12"
                }
            )
        }


class GroupeForm(forms.ModelForm):
    class Meta:
        model = Groupe
        fields = ["nom", "tranche_age", "capacite", "educateur"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        educateurs_disponibles = Educateur.objects.filter(
            groupe__isnull=True
        )

        if self.instance and self.instance.pk:
            educateur_actuel = self.instance.educateur

            if educateur_actuel is not None:
                educateurs_disponibles = (
                    educateurs_disponibles
                    | Educateur.objects.filter(pk=educateur_actuel.pk)
                )

        self.fields["educateur"].queryset = educateurs_disponibles

        self.aucun_educateur_disponible = (
            not educateurs_disponibles.exists()
        )


class PhotoFileInput(forms.ClearableFileInput):
    """
    ClearableFileInput sans le texte "Actuellement : <lien>" par défaut de Django :
    la photo actuelle est déjà affichée en aperçu par le template, donc seule la
    case à cocher "Supprimer la photo actuelle" (quand une photo existe) est utile ici.
    """
    template_name = "widgets/photo_file_input.html"


class ActiviteForm(forms.ModelForm):
    class Meta:
        model = Activite
        fields = ["nom", "date", "lieu", "frais_inscription", "description", "photo", "groupes"]

        labels = {
            "nom": "Nom de l'activité",
            "date": "Date",
            "lieu": "Lieu",
            "frais_inscription": "Frais d'inscription ($)",
            "description": "Description",
            "photo": "Photo",
            "groupes": "Groupes concernés",
        }

        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Décrivez l'activité."
            }),
            "photo": PhotoFileInput(),
            "groupes": forms.CheckboxSelectMultiple(),
        }

        error_messages = {
            "nom": {"required": "Veuillez indiquer le nom de l'activité."},
            "date": {"required": "Veuillez indiquer la date de l'activité."},
            "lieu": {"required": "Veuillez indiquer le lieu de l'activité."},
            "frais_inscription": {"required": "Veuillez indiquer les frais d'inscription."},
            "description": {"required": "Veuillez indiquer une description de l'activité."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name != "groupes":
                field.widget.attrs.setdefault("class", "form-control")


class AccepterDemandeInscriptionForm(forms.Form):
    groupe = forms.ModelChoiceField(
        queryset=Groupe.objects.none(),
        label="Groupe",
        empty_label="Sélectionnez un groupe",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["groupe"].queryset = (
            Groupe.objects.filter(educateur__isnull=False)
            .annotate(nb_enfants=Count("enfant"))
            .filter(nb_enfants__lt=F("capacite"))
        )
