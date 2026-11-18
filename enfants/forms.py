import re

from django import forms
from django.utils import timezone
from django.db.models import Count, F

from .models import (
    Activite,
    Allergie,
    ContactUrgence,
    Groupe,
    PersonneAutorisee,
    DemandeInscription,
    Presence,
    Enfant,
)

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
                "required": (
                    "Veuillez préciser la réaction provoquée "
                    "par cette allergie."
                )
            },
        }

        widgets = {
            "reaction": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Décrivez la réaction provoquée par l'allergie."
                    ),
                }
            )
        }


class DemandeInscriptionForm(forms.ModelForm):
    class Meta:
        model = DemandeInscription
        fields = [
            "prenom_enfant",
            "nom_enfant",
            "date_naissance",
            "note",
        ]

        labels = {
            "prenom_enfant": "Prénom de l'enfant",
            "nom_enfant": "Nom de l'enfant",
            "date_naissance": "Date de naissance",
            "note": "Note (optionnelle)",
        }

        widgets = {
            "prenom_enfant": forms.TextInput(
                attrs={
                    "placeholder": "Prénom de l'enfant"
                }
            ),
            "nom_enfant": forms.TextInput(
                attrs={
                    "placeholder": "Nom de l'enfant"
                }
            ),
            "date_naissance": forms.DateInput(
                attrs={"type": "date"}
            ),
            "note": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Informations complémentaires pour "
                        "l'administration (optionnel)."
                    ),
                }
            ),
        }

        error_messages = {
            "prenom_enfant": {
                "required": (
                    "Veuillez indiquer le prénom de l'enfant."
                )
            },
            "nom_enfant": {
                "required": (
                    "Veuillez indiquer le nom de l'enfant."
                )
            },
            "date_naissance": {
                "required": (
                    "Veuillez indiquer la date de naissance de l'enfant."
                )
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "form-control"
            )


class ContactUrgenceForm(forms.ModelForm):
    class Meta:
        model = ContactUrgence
        fields = [
            "prenom",
            "nom",
            "telephone",
        ]

        error_messages = {
            "prenom": {
                "required": (
                    "Veuillez indiquer le prénom du contact d'urgence."
                )
            },
            "nom": {
                "required": (
                    "Veuillez indiquer le nom du contact d'urgence."
                )
            },
            "telephone": {
                "required": (
                    "Veuillez indiquer un numéro de téléphone "
                    "pour joindre cette personne."
                )
            },
        }

        widgets = {
            "telephone": forms.TextInput(
                attrs={
                    "placeholder": "418-555-1234",
                    "maxlength": "12",
                }
            )
        }


class PersonneAutoriseeForm(forms.ModelForm):
    class Meta:
        model = PersonneAutorisee
        fields = [
            "prenom",
            "nom",
            "relation",
            "telephone",
        ]

        error_messages = {
            "prenom": {
                "required": (
                    "Veuillez indiquer le prénom "
                    "de la personne autorisée."
                )
            },
            "nom": {
                "required": (
                    "Veuillez indiquer le nom "
                    "de la personne autorisée."
                )
            },
            "relation": {
                "required": (
                    "Veuillez préciser le lien entre l'enfant "
                    "et la personne autorisée."
                )
            },
            "telephone": {
                "required": (
                    "Veuillez indiquer un numéro de téléphone "
                    "pour joindre cette personne."
                )
            },
        }

        widgets = {
            "telephone": forms.TextInput(
                attrs={
                    "placeholder": "418-555-1234",
                    "maxlength": "12",
                }
            )
        }


class GroupeForm(forms.ModelForm):
    class Meta:
        model = Groupe
        fields = [
            "nom",
            "tranche_age",
            "capacite",
            "educateur",
        ]

        labels = {
            "nom": "Nom",
            "tranche_age": "Tranche d'âge",
            "capacite": "Capacité",
            "educateur": "Éducateur",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "form-control"
            )

        educateurs_disponibles = Educateur.objects.filter(
            groupe__isnull=True
        )

        if self.instance and self.instance.pk:
            educateur_actuel = self.instance.educateur

            if educateur_actuel is not None:
                educateurs_disponibles = (
                    educateurs_disponibles
                    | Educateur.objects.filter(
                        pk=educateur_actuel.pk
                    )
                )

        self.fields[
            "educateur"
        ].queryset = educateurs_disponibles

        self.aucun_educateur_disponible = (
            not educateurs_disponibles.exists()
        )

    def clean_educateur(self):
        educateur = self.cleaned_data.get("educateur")

        if (
            self.instance
            and self.instance.pk
            and educateur is None
        ):
            if self.instance.enfant_set.exists():
                raise forms.ValidationError(
                    "Impossible de retirer l'éducateur : "
                    "ce groupe a encore des enfants assignés."
                )

        return educateur


class PhotoFileInput(forms.ClearableFileInput):
    """
    ClearableFileInput sans le texte
    "Actuellement : <lien>" par défaut de Django.

    La photo actuelle est déjà affichée en aperçu par le template,
    donc seule la case à cocher "Supprimer la photo actuelle"
    est utile ici.
    """

    template_name = "widgets/photo_file_input.html"


class ActiviteForm(forms.ModelForm):
    class Meta:
        model = Activite

        fields = [
            "nom",
            "date",
            "heure_debut",     
            "heure_fin",       
            "lieu",
            "frais_inscription",
            "places_disponibles",
            "description",
            "photo",
            "groupes",
        ]

        labels = {
            "nom": "Nom de l'activité",
            "date": "Date",
            "heure_debut": "Heure de début",
            "heure_fin": "Heure de fin",
            "lieu": "Lieu",
            "frais_inscription": "Frais d'inscription ($)",
            "places_disponibles": (
                "Nombre de places disponibles"
            ),
            "description": "Description",
            "photo": "Photo",
            "groupes": "Groupes concernés",
        }

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "heure_debut": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "heure_fin": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "places_disponibles": forms.NumberInput(
                attrs={"min": "1"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Décrivez l'activité.",
                }
            ),
            "photo": PhotoFileInput(),
            "groupes": forms.CheckboxSelectMultiple(),
        }

        error_messages = {
            "nom": {
                "required": (
                    "Veuillez indiquer le nom de l'activité."
                )
            },
            "date": {
                "required": (
                    "Veuillez indiquer la date de l'activité."
                )
            },
            "heure_debut": {
                "required": "Veuillez indiquer l'heure de début de l'activité."
            },
            "heure_fin": {
                "required": "Veuillez indiquer l'heure de fin de l'activité."
            },
            "lieu": {
                "required": (
                    "Veuillez indiquer le lieu de l'activité."
                )
            },
            "frais_inscription": {
                "required": (
                    "Veuillez indiquer les frais d'inscription."
                )
            },
            "places_disponibles": {
                "required": (
                    "Veuillez indiquer le nombre de places disponibles."
                )
            },
            "description": {
                "required": (
                    "Veuillez indiquer une description de l'activité."
                )
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name != "groupes":
                field.widget.attrs.setdefault(
                    "class",
                    "form-control"
                )

        self.fields["places_disponibles"].widget.attrs["min"] = "1"
        self.fields["heure_debut"].required = True
        self.fields["heure_fin"].required = True

class AccepterDemandeInscriptionForm(forms.Form):
    groupe = forms.ModelChoiceField(
        queryset=Groupe.objects.none(),
        label="Groupe",
        empty_label="Sélectionnez un groupe",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["groupe"].queryset = (
            Groupe.objects
            .filter(educateur__isnull=False)
            .annotate(
                nb_enfants=Count("enfant")
            )
            .filter(
                nb_enfants__lt=F("capacite")
            )
        )


class PaiementCarteForm(forms.Form):
    numero_carte = forms.CharField(
        label="Numéro de carte",
        max_length=19,
        widget=forms.TextInput(attrs={"placeholder": "1234 5678 9012 3456"}),
        error_messages={"required": "Veuillez indiquer le numéro de carte."},
    )
    expiration = forms.CharField(
        label="Expiration",
        max_length=5,
        widget=forms.TextInput(attrs={"placeholder": "MM/AA"}),
        error_messages={"required": "Veuillez indiquer la date d'expiration de la carte."},
    )
    cvv = forms.CharField(
        label="CVV",
        max_length=4,
        widget=forms.TextInput(attrs={"placeholder": "123"}),
        error_messages={"required": "Veuillez indiquer le code CVV de la carte."},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_numero_carte(self):
        valeur = self.cleaned_data["numero_carte"]
        chiffres = valeur.replace(" ", "")

        if not chiffres.isdigit():
            raise forms.ValidationError("Le numéro de carte ne doit contenir que des chiffres.")

        if len(chiffres) < 13 or len(chiffres) > 19:
            raise forms.ValidationError("Le numéro de carte doit contenir entre 13 et 19 chiffres.")

        return valeur

    def clean_expiration(self):
        valeur = self.cleaned_data["expiration"]

        if not re.fullmatch(r"(0[1-9]|1[0-2])/\d{2}", valeur):
            raise forms.ValidationError("La date d'expiration doit être au format MM/AA.")

        return valeur

    def clean_cvv(self):
        valeur = self.cleaned_data["cvv"]

        if not re.fullmatch(r"\d{3,4}", valeur):
            raise forms.ValidationError("Le code CVV doit contenir 3 ou 4 chiffres.")

        return valeur


class PresenceParentForm(forms.ModelForm):
    class Meta:
        model = Presence

        fields = [
            "enfant",
            "type",
            "date",
            "date_fin",
            "heure",
            "heure_fin",
            "motif",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "date_fin": forms.DateInput(
                attrs={"type": "date"}
            ),
            "heure": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "heure_fin": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "motif": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Indiquez le motif du signalement."
                    ),
                }
            ),
        }

        labels = {
            "enfant": "Enfant",
            "type": "Type de signalement",
            "date": "Date de début",
            "date_fin": "Date de fin",
            "heure": "Heure de début",
            "heure_fin": "Heure de fin",
            "motif": "Motif",
        }

    def __init__(
        self,
        *args,
        parent=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        if parent is not None:
            self.fields["enfant"].queryset = (
                Enfant.objects.filter(
                    parents=parent
                )
            )

        self.fields["date_fin"].help_text = (
            "Laissez vide pour une absence d'une seule journée. "
            "Pour un retard, la date de fin correspond "
            "automatiquement à la date de début."
        )

        self.fields["heure_fin"].help_text = (
            "Obligatoire pour un retard. "
            "Laissez vide pour une absence."
        )

    def clean_date(self):
        date = self.cleaned_data.get("date")

        # À la création, le parent ne peut pas
        # signaler une présence pour une date passée.
        # En modification, on autorise une date passée :
        # la vue vérifie si la période est encore en cours.
        if (
            not self.instance.pk
            and date
            and date < timezone.now().date()
        ):
            raise forms.ValidationError(
                "Vous ne pouvez pas signaler une absence "
                "ou un retard pour une date passée."
            )

        return date

    def clean(self):
        cleaned_data = super().clean()

        type_presence = cleaned_data.get("type")
        date_debut = cleaned_data.get("date")
        date_fin = cleaned_data.get("date_fin")
        heure_debut = cleaned_data.get("heure")
        heure_fin = cleaned_data.get("heure_fin")

        if (
            type_presence == Presence.Type.RETARD
            and date_debut
        ):
            cleaned_data["date_fin"] = date_debut

        elif (
            date_debut
            and date_fin
            and date_fin < date_debut
        ):
            self.add_error(
                "date_fin",
                "La date de fin doit être égale "
                "ou postérieure à la date de début."
            )

        if type_presence == Presence.Type.RETARD:
            if not heure_fin:
                self.add_error(
                    "heure_fin",
                    "L'heure de fin est obligatoire pour un retard."
                )

            elif (
                heure_debut
                and heure_fin <= heure_debut
            ):
                self.add_error(
                    "heure_fin",
                    "L'heure de fin doit être postérieure "
                    "à l'heure de début."
                )

        else:
            cleaned_data["heure_fin"] = None

        return cleaned_data


class PresenceEducateurForm(forms.ModelForm):
    class Meta:
        model = Presence

        fields = [
            "enfant",
            "type",
            "date",
            "date_fin",
            "heure",
            "heure_fin",
            "motif",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "date_fin": forms.DateInput(
                attrs={"type": "date"}
            ),
            "heure": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "heure_fin": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "motif": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Indiquez le motif du signalement."
                    ),
                }
            ),
        }

        labels = {
            "enfant": "Enfant",
            "type": "Type de présence",
            "date": "Date de début",
            "date_fin": "Date de fin",
            "heure": "Heure de début",
            "heure_fin": "Heure de fin",
            "motif": "Motif",
        }

    def __init__(
        self,
        *args,
        educateur=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        if educateur is not None:
            self.fields["enfant"].queryset = (
                Enfant.objects.filter(
                    groupe__educateur=educateur
                )
            )

        self.fields["date_fin"].help_text = (
            "Laissez vide pour une absence d'une seule journée. "
            "Pour un retard, la date de fin correspond "
            "automatiquement à la date de début."
        )

        self.fields["heure_fin"].help_text = (
            "Obligatoire pour un retard. "
            "Laissez vide pour une absence."
        )

    def clean_date(self):
        date = self.cleaned_data.get("date")

        if (
            date
            and date > timezone.now().date()
        ):
            raise forms.ValidationError(
                "Vous ne pouvez pas enregistrer une absence "
                "ou un retard pour une date future."
            )

        return date

    def clean(self):
        cleaned_data = super().clean()

        type_presence = cleaned_data.get("type")
        date_debut = cleaned_data.get("date")
        date_fin = cleaned_data.get("date_fin")
        heure_debut = cleaned_data.get("heure")
        heure_fin = cleaned_data.get("heure_fin")

        if (
            type_presence == Presence.Type.RETARD
            and date_debut
        ):
            cleaned_data["date_fin"] = date_debut

        elif (
            date_debut
            and date_fin
            and date_fin < date_debut
        ):
            self.add_error(
                "date_fin",
                "La date de fin doit être égale "
                "ou postérieure à la date de début."
            )

        if type_presence == Presence.Type.RETARD:
            if not heure_fin:
                self.add_error(
                    "heure_fin",
                    "L'heure de fin est obligatoire pour un retard."
                )

            elif (
                heure_debut
                and heure_fin <= heure_debut
            ):
                self.add_error(
                    "heure_fin",
                    "L'heure de fin doit être postérieure "
                    "à l'heure de début."
                )

        else:
            cleaned_data["heure_fin"] = None

        return cleaned_data


class PresenceAdminForm(forms.ModelForm):
    groupe = forms.ModelChoiceField(
        queryset=Groupe.objects.order_by("nom"),
        label="Groupe",
        empty_label="Sélectionnez un groupe",
    )

    class Meta:
        model = Presence

        fields = [
            "groupe",
            "enfant",
            "type",
            "date",
            "date_fin",
            "heure",
            "heure_fin",
            "motif",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "date_fin": forms.DateInput(
                attrs={"type": "date"}
            ),
            "heure": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "heure_fin": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "motif": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Indiquez le motif du signalement."
                    ),
                }
            ),
        }

        labels = {
            "enfant": "Enfant",
            "type": "Type de signalement",
            "date": "Date de début",
            "date_fin": "Date de fin",
            "heure": "Heure de début",
            "heure_fin": "Heure de fin",
            "motif": "Motif",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["date_fin"].help_text = (
            "Laissez vide pour une absence d'une seule journée. "
            "Pour un retard, la date de fin correspond "
            "automatiquement à la date de début."
        )

        self.fields["heure_fin"].help_text = (
            "Obligatoire pour un retard. "
            "Laissez vide pour une absence."
        )

        self.fields[
            "enfant"
        ].queryset = Enfant.objects.none()

        groupe_id = None

        if self.is_bound:
            groupe_id = self.data.get("groupe")

        elif self.instance and self.instance.pk:
            groupe_id = (
                self.instance.enfant.groupe_id
            )

            self.fields[
                "groupe"
            ].initial = groupe_id

        if groupe_id:
            try:
                self.fields["enfant"].queryset = (
                    Enfant.objects
                    .filter(
                        groupe_id=groupe_id
                    )
                    .order_by(
                        "nom",
                        "prenom"
                    )
                )

            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()

        groupe = cleaned_data.get("groupe")
        enfant = cleaned_data.get("enfant")
        type_presence = cleaned_data.get("type")
        date_debut = cleaned_data.get("date")
        date_fin = cleaned_data.get("date_fin")
        heure_debut = cleaned_data.get("heure")
        heure_fin = cleaned_data.get("heure_fin")

        if (
            groupe
            and enfant
            and enfant.groupe_id != groupe.id
        ):
            self.add_error(
                "enfant",
                "Cet enfant n'appartient pas "
                "au groupe sélectionné."
            )

        if (
            type_presence == Presence.Type.RETARD
            and date_debut
        ):
            cleaned_data["date_fin"] = date_debut

        elif (
            date_debut
            and date_fin
            and date_fin < date_debut
        ):
            self.add_error(
                "date_fin",
                "La date de fin doit être égale "
                "ou postérieure à la date de début."
            )

        if type_presence == Presence.Type.RETARD:
            if not heure_fin:
                self.add_error(
                    "heure_fin",
                    "L'heure de fin est obligatoire pour un retard."
                )

            elif (
                heure_debut
                and heure_fin <= heure_debut
            ):
                self.add_error(
                    "heure_fin",
                    "L'heure de fin doit être postérieure "
                    "à l'heure de début."
                )

        else:
            cleaned_data["heure_fin"] = None

        return cleaned_data
