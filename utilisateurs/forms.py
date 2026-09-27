from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CreationCompteForm(UserCreationForm):
   

    email = forms.EmailField(required=True, label="Courriel")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "telephone",
        ]
        labels = {
            "username": "Nom d'utilisateur",
            "first_name": "Prénom",
            "last_name": "Nom",
            "role": "Rôle",
            "telephone": "Téléphone",
        }

   
    AIDE_CHAMPS = {
        "username": "Veuillez choisir un nom d'utilisateur.",
        "first_name": "Veuillez entrer le prénom.",
        "last_name": "Veuillez entrer le nom.",
        "email": "Veuillez entrer l'adresse courriel.",
        "role": "Veuillez choisir le rôle que voulez attribuer.",
        "telephone": "",
        "password1": "Veuillez choisir un mot de passe.",
        "password2": "Veuillez confirmer le mot de passe.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            field.help_text = self.AIDE_CHAMPS.get(name, "")

        
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmation du mot de passe"

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec ce courriel.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
