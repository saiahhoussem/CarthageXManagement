from django import forms
from .models import Enfant, Allergie, ContactUrgence, PersonneAutorisee


class EnfantForm(forms.ModelForm):
    class Meta:
        model = Enfant
        fields = ["nom", "groupe", "date_naissance"]

class AllergieForm(forms.ModelForm):
    class Meta:
        model = Allergie
        fields = ["type_allergie", "reaction"]


class ContactUrgenceForm(forms.ModelForm):
    class Meta:
        model = ContactUrgence
        fields = ["nom", "telephone"]


class PersonneAutoriseeForm(forms.ModelForm):
    class Meta:
        model = PersonneAutorisee
        fields = ["nom", "relation", "telephone"]