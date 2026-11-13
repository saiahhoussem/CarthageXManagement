from django import forms
from django.utils import timezone
from django.db.models import Count, F

from .models import Activite, Allergie, ContactUrgence, Groupe, PersonneAutorisee, DemandeInscription, Presence, Enfant
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
        fields = [
            "nom", 
            "tranche_age", 
            "capacite", 
            "educateur"
            ]
        labels ={
            "nom":"Nom", 
            "tranche_age":"Tranche d'âge", 
            "capacite":"Capacité", 
            "educateur":"Éducateur",
            }

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

    def clean_educateur(self):
        educateur = self.cleaned_data.get("educateur")

        if self.instance and self.instance.pk and educateur is None:
            if self.instance.enfant_set.exists():
                raise forms.ValidationError(
                    "Impossible de retirer l'éducateur : ce groupe a encore des enfants assignés."
                )

        return educateur


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
        fields = ["nom", "date", "lieu", "frais_inscription", "places_disponibles", "description", "photo", "groupes"]

        labels = {
            "nom": "Nom de l'activité",
            "date": "Date",
            "lieu": "Lieu",
            "frais_inscription": "Frais d'inscription ($)",
            "places_disponibles": "Nombre de places disponibles",
            "description": "Description",
            "photo": "Photo",
            "groupes": "Groupes concernés",
        }

        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "places_disponibles": forms.NumberInput(attrs={"min": "1"}),
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
            "places_disponibles": {"required": "Veuillez indiquer le nombre de places disponibles."},
            "description": {"required": "Veuillez indiquer une description de l'activité."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name != "groupes":
                field.widget.attrs.setdefault("class", "form-control")

        # PositiveIntegerField force min="0" sur le widget par défaut (son
        # propre plancher), ce qui écrase l'attribut "min" du widget passé
        # dans Meta.widgets. On le corrige ici pour refléter le vrai
        # minimum métier (MinValueValidator(1) sur le modèle).
        self.fields["places_disponibles"].widget.attrs["min"] = "1"


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

class PresenceParentForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = [
            "enfant",
            "type",
            "date",
            "date_fin",
            "heure",
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
            "motif": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Indiquez le motif du signalement."
                }
            ),
        }

        labels = {
            "enfant": "Enfant",
            "type": "Type de signalement",
            "date": "Date de début",
            "date_fin": "Date de fin",
            "heure": "Heure",
            "motif": "Motif",
        }

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)

        if parent is not None:
            self.fields["enfant"].queryset = Enfant.objects.filter(
                parents=parent
            )

        self.fields["date_fin"].help_text = (
            "Laissez vide pour un signalement d'absence d'une seule journée."
            "Si vous signalez un retard, elle ne doit pas être remplie."
        )

    def clean_date(self):
        date = self.cleaned_data.get("date")

        if date and date < timezone.now().date():
            raise forms.ValidationError(
                "Vous ne pouvez pas signaler une absence ou un retard "
                "pour une date passée."
            )

        return date

    def clean(self):
        cleaned_data = super().clean()

        type_presence = cleaned_data.get("type")
        date_debut = cleaned_data.get("date")
        date_fin = cleaned_data.get("date_fin")

        if date_debut and date_fin and date_fin < date_debut:
            self.add_error(
                "date_fin",
                "La date de fin doit être égale ou postérieure "
                "à la date de début."
            )

        if (
            type_presence == Presence.Type.RETARD
            and date_fin
        ):
            self.add_error(
                "date_fin",
                "La date de fin n'est pas nécessaire pour un retard."
            )

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
            "motif": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Indiquez le motif du signalement."
                }
            ),
        }

        labels = {
            "enfant": "Enfant",
            "type": "Type de présence",
            "date": "Date de début",
            "date_fin": "Date de fin",
            "heure": "Heure",
            "motif": "Motif",
        }

    def __init__(self, *args, educateur=None, **kwargs):
        super().__init__(*args, **kwargs)

        if educateur is not None:
            self.fields["enfant"].queryset = Enfant.objects.filter(
                groupe__educateur=educateur
            )

    def clean_date(self):
        date = self.cleaned_data.get("date")

        if date and date > timezone.now().date():
            raise forms.ValidationError(
                "Vous ne pouvez pas enregistrer une absence ou un retard "
                "pour une date future."
            )

        return date

    def clean(self):
        cleaned_data = super().clean()

        type_presence = cleaned_data.get("type")
        date_debut = cleaned_data.get("date")
        date_fin = cleaned_data.get("date_fin")

        if date_debut and date_fin and date_fin < date_debut:
            self.add_error(
                "date_fin",
                "La date de fin doit être égale ou postérieure "
                "à la date de début."
            )

        if (
            type_presence == Presence.Type.RETARD
            and date_fin
        ):
            self.add_error(
                "date_fin",
                "La date de fin n'est pas nécessaire pour un retard."
            )

        return cleaned_data

class PresenceAdminForm(forms.ModelForm):
    groupe = forms.ModelChoiceField(
        queryset=Groupe.objects.order_by("nom"),
        label="Groupe",
        empty_label="Sélectionnez un groupe"
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
            "motif": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Indiquez le motif du signalement."
                }
            ),
        }

        labels = {
            "enfant": "Enfant",
            "type": "Type de signalement",
            "date": "Date de début",
            "date_fin": "Date de fin",
            "heure": "Heure",
            "motif": "Motif",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["date_fin"].help_text = (
            "Laissez vide pour une absence d'une seule journée. "
            "Non applicable pour un retard."
        )

        self.fields["enfant"].queryset = Enfant.objects.none()

        groupe_id = None

        if self.is_bound:
            groupe_id = self.data.get("groupe")

        elif self.instance and self.instance.pk:
            groupe_id = self.instance.enfant.groupe_id
            self.fields["groupe"].initial = groupe_id

        if groupe_id:
            try:
                self.fields["enfant"].queryset = (
                    Enfant.objects
                    .filter(groupe_id=groupe_id)
                    .order_by("nom", "prenom")
                )
            except (ValueError, TypeError):
                pass

    def clean_date(self):
        date = self.cleaned_data.get("date")

        if date and date < timezone.now().date():
            raise forms.ValidationError(
                "Vous ne pouvez pas enregistrer un signalement "
                "pour une date passée."
            )

        return date

    def clean(self):
        cleaned_data = super().clean()

        groupe = cleaned_data.get("groupe")
        enfant = cleaned_data.get("enfant")
        type_presence = cleaned_data.get("type")
        date_debut = cleaned_data.get("date")
        date_fin = cleaned_data.get("date_fin")

        if groupe and enfant and enfant.groupe_id != groupe.id:
            self.add_error(
                "enfant",
                "Cet enfant n'appartient pas au groupe sélectionné."
            )

        if date_debut and date_fin and date_fin < date_debut:
            self.add_error(
                "date_fin",
                "La date de fin doit être égale ou postérieure "
                "à la date de début."
            )

        if type_presence == Presence.Type.RETARD and date_fin:
            self.add_error(
                "date_fin",
                "La date de fin n'est pas nécessaire pour un retard."
            )

        return cleaned_data