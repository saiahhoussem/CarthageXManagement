from django import forms
from .models import Enfant, Allergie, ContactUrgence, PersonneAutorisee


class EnfantForm(forms.ModelForm):
    class Meta:
        model = Enfant
        fields = ["prenom", "nom", "groupe", "date_naissance"]

        error_messages = {
            "prenom": {"required": "Veuillez indiquer le prénom de l'enfant."},
            "nom": {"required": "Veuillez indiquer le nom de l'enfant."},
            "date_naissance": { "required": "Veuillez indiquer la date de naissance de l'enfant."}
        }

class AllergieForm(forms.ModelForm):
    class Meta:
        model = Allergie
        fields = ["type_allergie", "reaction"]

        widgets = {
            "reaction": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Décrivez la réaction provoquée par l'allergie."
            })
        }

        error_messages = {
            "type_allergie": {"required": "Le type de l'allergie est obligatoire."},
            "reaction": {"required": "Veuillez préciser la réaction provoquée par cette allergie."}
        }

class ContactUrgenceForm(forms.ModelForm):
    class Meta:
        model = ContactUrgence
        fields = ["prenom", "nom", "telephone"]

        error_messages = {
            "prenom": {"required": "Veuillez indiquer le prénom du contact d'urgence."},
            "nom": {"required": "Veuillez indiquer le nom du contact d'urgence." }, 
            "telephone": {"required": "Veuillez indiquer un numéro de téléphone pour joindre cette personne." } 
            }
        widgets = { "telephone": forms.TextInput(attrs={ "placeholder": "418-555-1234", "maxlength": "12" }) }

class PersonneAutoriseeForm(forms.ModelForm):
    class Meta:
        model = PersonneAutorisee
        fields = ["prenom", "nom", "relation", "telephone"]
        error_messages = { 
            "prenom": { "required": "Veuillez indiquer le prénom de la personne autorisée."},
            "nom": { "required": "Veuillez indiquer le nom de la personne autorisée." }, 
            "relation": { "required": "Veuillez préciser le lien entre l'enfant et la personne autorisée." }, 
            "telephone": { "required": "Veuillez indiquer un numéro de téléphone pour joindre cette personne." } 
            }
        widgets = { "telephone": forms.TextInput(attrs={ "placeholder": "418-555-1234", "maxlength": "12" }) }