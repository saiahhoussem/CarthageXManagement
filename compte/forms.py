from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Administrateur, Educateur, Parent, User


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(
        label="Adresse courriel ou nom d'utilisateur",
        widget=forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    se_souvenir = forms.BooleanField(
        label="Se souvenir de moi",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


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
        "first_name": "Veuillez entrer le prénom de l'utilisateur.",
        "last_name": "Veuillez entrer le nom de l'utilisateur.",
        "email": "Veuillez entrer l'adresse courriel de l'utilisateur.",
        "role": "Veuillez choisir le rôle que voulez attribuer à l'utilisateur.",
        "telephone": "Veuillez entrer le numéro de téléphone de l'utilisateur.",
        "password1": "Veuillez choisir un mot de passe du compte.",
        "password2": "Veuillez confirmer le mot de passe du compte.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            field.help_text = self.AIDE_CHAMPS.get(name, "")
            field.required = True

        
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmation du mot de passe"

    ROLE_MODELES = {
        User.Role.ADMINISTRATEUR: Administrateur,
        User.Role.EDUCATEUR: Educateur,
        User.Role.PARENT: Parent,
    }

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec ce courriel.")
        return email

    def save(self, commit=True):
        modele = self.ROLE_MODELES.get(self.cleaned_data["role"], User)
        utilisateur = modele(
            username=self.cleaned_data["username"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
            role=self.cleaned_data["role"],
            telephone=self.cleaned_data["telephone"],
        )
        utilisateur.set_password(self.cleaned_data["password1"])
        if commit:
            utilisateur.save()
        return utilisateur
