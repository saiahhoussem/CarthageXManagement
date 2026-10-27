from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Administrateur, Educateur, Parent, User

class ConnexionForm(AuthenticationForm):
    username = forms.CharField(
        label="Adresse courriel ou nom d'utilisateur",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "id": "id_password",
        }),
    )
    se_souvenir = forms.BooleanField(
        label="Se souvenir de moi",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

class BaseCreationCompteForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Courriel")

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "telephone",
        ]
        labels = {
            "username": "Nom d'utilisateur",
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Courriel",
            "telephone": "Téléphone",
        }

    AIDE_CHAMPS = {
        "username": "Veuillez choisir un nom d'utilisateur.",
        "first_name": "Veuillez entrer le prénom de l'utilisateur.",
        "last_name": "Veuillez entrer le nom de l'utilisateur.",
        "email": "Veuillez entrer l'adresse courriel de l'utilisateur.",
        "telephone": "Veuillez entrer le numéro de téléphone de l'utilisateur.",
        "password1": "Veuillez choisir un mot de passe du compte.",
        "password2": "Veuillez confirmer le mot de passe du compte.",
    }

    role = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Nom d'utilisateur"
        self.fields["first_name"].label = "Prénom"
        self.fields["last_name"].label = "Nom"
        self.fields["email"].label = "Courriel"
        self.fields["telephone"].label = "Téléphone"
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmation du mot de passe"

        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            field.help_text = self.AIDE_CHAMPS.get(name, "")
            field.required = True

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec ce courriel.")
        return email

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.role = self.role  
        if commit:
            utilisateur.save()
        return utilisateur

class CreationAdministrateurForm(BaseCreationCompteForm):
    role = User.Role.ADMINISTRATEUR

    class Meta(BaseCreationCompteForm.Meta):
        model = Administrateur
        fields = BaseCreationCompteForm.Meta.fields

class CreationEducateurForm(BaseCreationCompteForm):
    role = User.Role.EDUCATEUR

    class Meta(BaseCreationCompteForm.Meta):
        model = Educateur
        fields = BaseCreationCompteForm.Meta.fields

class CreationParentForm(BaseCreationCompteForm):
    role = User.Role.PARENT

    class Meta(BaseCreationCompteForm.Meta):
        model = Parent
        fields = BaseCreationCompteForm.Meta.fields


class BaseModificationCompteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "telephone"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "username": "Nom d'utilisateur",
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Courriel",
            "telephone": "Téléphone",
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Un compte existe déjà avec ce courriel.")
        return email

class ModificationParentForm(BaseModificationCompteForm):
    class Meta(BaseModificationCompteForm.Meta):
        model = Parent
        fields = BaseModificationCompteForm.Meta.fields


class ModificationEducateurForm(BaseModificationCompteForm):
    class Meta(BaseModificationCompteForm.Meta):
        model = Educateur
        fields = BaseModificationCompteForm.Meta.fields


class ModificationAdministrateurForm(BaseModificationCompteForm):
    class Meta(BaseModificationCompteForm.Meta):
        model = Administrateur
        fields = BaseModificationCompteForm.Meta.fields