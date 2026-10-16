from django import forms

from .models import Allergie, ContactUrgence, Groupe, PersonneAutorisee


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

        error_messages = {
            "nom": {
                "required": "Veuillez indiquer le nom du groupe."
            },
            "tranche_age": {
                "required": "Veuillez sélectionner une tranche d'âge."
            },
            "capacite": {
                "required": "Veuillez indiquer la capacité maximale du groupe.",
                "invalid": "Veuillez entrer un nombre valide."
            }
        }

        widgets = {
            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom du groupe"
                }
            ),
            "tranche_age": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
            "capacite": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Ex. : 10"
                }
            ),
            "educateur": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }