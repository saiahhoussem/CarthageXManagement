import unicodedata
from datetime import time, timedelta
from itertools import count
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from compte.models import Administrateur, Educateur, Parent, User
from enfants.models import (
    Activite,
    Allergie,
    ContactUrgence,
    DemandeInscription,
    Enfant,
    Groupe,
    InscriptionActivite,
    Paiement,
    PersonneAutorisee,
)

MOT_DE_PASSE_DEMO = "mdpcarthage123!"
NOM_FICHIER_IDENTIFIANTS = "comptes_carthagekids.txt"

COMPTEUR_TELEPHONE = count(1)


def enlever_accents(texte):
    normalise = unicodedata.normalize("NFKD", texte)
    return "".join(
        caractere
        for caractere in normalise
        if not unicodedata.combining(caractere)
    )


def generer_username(prenom, nom, usernames_existants):
    base = enlever_accents(f"{prenom[0]}{nom}").lower()
    base = "".join(
        caractere
        for caractere in base
        if caractere.isalnum()
    )

    username = base
    suffixe = 1

    while username in usernames_existants:
        suffixe += 1
        username = f"{base}{suffixe}"

    usernames_existants.add(username)
    return username


def generer_telephone():
    indice = next(COMPTEUR_TELEPHONE)
    return f"418-555-{1000 + indice:04d}"


def jour_passe(jours):
    return timezone.now().date() - timedelta(days=jours)


def jour_futur(jours):
    return timezone.now().date() + timedelta(days=jours)


class Command(BaseCommand):
    help = "Injecte un jeu de donnees de demonstration realiste dans la base."

    def handle(self, *args, **options):
        usernames_existants = set(
            User.objects.values_list("username", flat=True)
        )

        with transaction.atomic():
            administrateurs = self.creer_administrateurs(usernames_existants)
            educateurs = self.creer_educateurs(usernames_existants)
            groupes = self.creer_groupes(educateurs)
            familles = self.creer_parents(usernames_existants)
            enfants = self.creer_enfants(familles, groupes)
            self.creer_profils_enfants(enfants)
            activites = self.creer_activites(groupes)
            self.creer_inscriptions_et_paiements(activites, enfants)
            self.creer_demandes_inscription(familles)

        chemin_fichier = self.generer_fichier_identifiants(
            administrateurs,
            educateurs,
            familles,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Donnees de demonstration injectees avec succes. "
                f"Identifiants ecrits dans {chemin_fichier}"
            )
        )

    def creer_ou_recuperer_compte(self, modele, role, prenom, nom, usernames_existants, est_superuser=False):
        existant = modele.objects.filter(
            first_name=prenom,
            last_name=nom,
        ).first()

        if existant:
            return existant

        username = generer_username(prenom, nom, usernames_existants)

        compte = modele(
            username=username,
            first_name=prenom,
            last_name=nom,
            email=f"{username}@carthagekids-demo.ca",
            telephone=generer_telephone(),
            role=role,
            is_superuser=est_superuser,
            is_staff=est_superuser,
        )
        compte.set_password(MOT_DE_PASSE_DEMO)
        compte.full_clean()
        compte.save()

        return compte

    def creer_administrateurs(self, usernames_existants):
        donnees = [
            ("Sami", "Ben Youssef", True),
            ("Nadia", "Chouikha", False),
        ]

        return [
            self.creer_ou_recuperer_compte(
                Administrateur,
                User.Role.ADMINISTRATEUR,
                prenom,
                nom,
                usernames_existants,
                est_superuser=superuser,
            )
            for prenom, nom, superuser in donnees
        ]

    def creer_educateurs(self, usernames_existants):
        donnees = [
            ("Karim", "Haddad"),
            ("Lea", "Fortin"),
            ("Yasmine", "Bouzid"),
            ("Mathieu", "Gagnon"),
            ("Amira", "Trabelsi"),
        ]

        return [
            self.creer_ou_recuperer_compte(
                Educateur,
                User.Role.EDUCATEUR,
                prenom,
                nom,
                usernames_existants,
            )
            for prenom, nom in donnees
        ]

    def creer_groupes(self, educateurs):
        donnees = [
            ("Les Petits Poussins", Groupe.TrancheAge.BEBE, 8),
            ("Les Explorateurs", Groupe.TrancheAge.TROTTEUR, 10),
            ("Les Petits Curieux", Groupe.TrancheAge.TROTTEUR, 10),
            ("Les Grands Reveurs", Groupe.TrancheAge.PRESCOLAIRE, 12),
            ("Les Etoiles Filantes", Groupe.TrancheAge.PRESCOLAIRE, 12),
        ]

        groupes = []

        for (nom, tranche_age, capacite), educateur in zip(donnees, educateurs):
            groupe, _ = Groupe.objects.get_or_create(
                nom=nom,
                defaults={
                    "tranche_age": tranche_age,
                    "capacite": capacite,
                    "educateur": educateur,
                },
            )

            if groupe.educateur_id is None:
                groupe.educateur = educateur
                groupe.save(update_fields=["educateur"])

            groupes.append(groupe)

        return groupes

    def creer_parents(self, usernames_existants):
        donnees_familles = [
            [("Mehdi", "Khelifi"), ("Sarah", "Bergeron")],
            [("Antoine", "Lavoie"), ("Imen", "Saidi")],
            [("Oussama", "Jlassi"), ("Camille", "Dubois")],
            [("Olivier", "Pelletier"), ("Rania", "Mejri")],
            [("Houda", "Snoussi")],
            [("Catherine", "Roy")],
            [("Walid", "Abidi")],
            [("Genevieve", "Cote")],
            [("Khalil", "Mansour")],
            [("Marie-Eve", "Belanger")],
            [("Youssef", "Barhoumi")],
        ]

        familles = []

        for membres in donnees_familles:
            parents = [
                self.creer_ou_recuperer_compte(
                    Parent,
                    User.Role.PARENT,
                    prenom,
                    nom,
                    usernames_existants,
                )
                for prenom, nom in membres
            ]
            familles.append(parents)

        return familles

    def creer_enfants(self, familles, groupes):
        groupe_poussins, groupe_explorateurs, groupe_curieux, groupe_reveurs, groupe_etoiles = groupes

        donnees_enfants = [
            (0, "Yanis", "Khelifi", 420, groupe_poussins),
            (0, "Nour", "Khelifi", 760, groupe_explorateurs),
            (1, "Leo", "Lavoie", 820, groupe_explorateurs),
            (2, "Mila", "Jlassi", 950, groupe_curieux),
            (2, "Adam", "Jlassi", 1050, groupe_curieux),
            (3, "Zoe", "Pelletier", 1450, groupe_reveurs),
            (4, "Aymen", "Snoussi", 480, groupe_poussins),
            (5, "Noah", "Roy", 700, groupe_explorateurs),
            (6, "Rayan", "Abidi", 980, groupe_curieux),
            (7, "Clara", "Cote", 1380, groupe_reveurs),
            (7, "Jade", "Cote", 1600, groupe_etoiles),
            (8, "Lina", "Mansour", 1700, groupe_etoiles),
            (9, "Emile", "Belanger", 360, groupe_poussins),
            (10, "Sofia", "Barhoumi", 1550, groupe_etoiles),
            (10, "Malak", "Barhoumi", 1400, groupe_reveurs),
        ]

        enfants = []

        for indice_famille, prenom, nom, age_jours, groupe in donnees_enfants:
            enfant, cree = Enfant.objects.get_or_create(
                prenom=prenom,
                nom=nom,
                defaults={
                    "groupe": groupe,
                    "date_naissance": jour_passe(age_jours),
                },
            )

            if cree:
                enfant.full_clean()
                enfant.save()

            enfant.parents.set(familles[indice_famille])
            enfants.append(enfant)

        return enfants

    def creer_profils_enfants(self, enfants):
        donnees_allergies = {
            "Yanis": ("Arachides", "Eruption cutanee et gonflement du visage."),
            "Mila": ("Lait de vache", "Troubles digestifs et inconfort."),
            "Rayan": ("Oeufs", "Urticaire localisee."),
            "Jade": ("Fruits de mer", "Gonflement des levres."),
            "Emile": ("Pollen", "Eternuements et yeux larmoyants."),
        }

        for enfant in enfants:
            if enfant.prenom in donnees_allergies and not enfant.allergie_set.exists():
                type_allergie, reaction = donnees_allergies[enfant.prenom]
                Allergie.objects.create(
                    enfant=enfant,
                    type_allergie=type_allergie,
                    reaction=reaction,
                )

            if not enfant.contacturgence_set.exists():
                ContactUrgence.objects.create(
                    enfant=enfant,
                    prenom="Grand-parent",
                    nom=enfant.nom,
                    telephone=generer_telephone(),
                )

            if not enfant.personneautorisee_set.exists():
                PersonneAutorisee.objects.create(
                    enfant=enfant,
                    prenom="Tante ou oncle",
                    nom=enfant.nom,
                    relation="Membre de la famille",
                    telephone=generer_telephone(),
                )

    def creer_activites(self, groupes):
        groupe_poussins, groupe_explorateurs, groupe_curieux, groupe_reveurs, groupe_etoiles = groupes

        donnees = [
            {
                "nom": "Journee des couleurs",
                "date": jour_futur(10),
                "lieu": "Salle polyvalente",
                "frais_inscription": 0,
                "places_disponibles": 40,
                "heure_debut": time(9, 0),
                "heure_fin": time(11, 0),
                "description": "Une journee ludique autour des couleurs et de la creativite.",
                "groupes": [],
                "annulee": False,
            },
            {
                "nom": "Sortie a la cabane a sucre",
                "date": jour_futur(25),
                "lieu": "Erabliere Lavoie, Shawinigan",
                "frais_inscription": 15,
                "places_disponibles": 20,
                "heure_debut": time(9, 0),
                "heure_fin": time(15, 0),
                "description": "Une sortie printaniere pour decouvrir la cabane a sucre.",
                "groupes": [groupe_explorateurs, groupe_curieux],
                "annulee": False,
            },
            {
                "nom": "Atelier de peinture",
                "date": jour_futur(5),
                "lieu": "Local d'arts",
                "frais_inscription": 5,
                "places_disponibles": 30,
                "heure_debut": time(13, 0),
                "heure_fin": time(14, 30),
                "description": "Un atelier de peinture libre pour tous les groupes.",
                "groupes": [],
                "annulee": False,
            },
            {
                "nom": "Fete de fin d'annee",
                "date": jour_futur(40),
                "lieu": "Cour exterieure",
                "frais_inscription": 0,
                "places_disponibles": 60,
                "heure_debut": time(10, 0),
                "heure_fin": time(16, 0),
                "description": "La grande fete annuelle avec jeux et animations.",
                "groupes": [],
                "annulee": False,
            },
            {
                "nom": "Visite a la ferme educative",
                "date": jour_futur(18),
                "lieu": "Ferme Au Grand Air",
                "frais_inscription": 20,
                "places_disponibles": 18,
                "heure_debut": time(8, 30),
                "heure_fin": time(14, 0),
                "description": "Decouverte des animaux de la ferme pour les plus grands.",
                "groupes": [groupe_reveurs, groupe_etoiles],
                "annulee": False,
            },
            {
                "nom": "Spectacle de marionnettes",
                "date": jour_passe(15),
                "lieu": "Auditorium",
                "frais_inscription": 8,
                "places_disponibles": 50,
                "heure_debut": time(10, 0),
                "heure_fin": time(11, 0),
                "description": "Un spectacle de marionnettes pour petits et grands.",
                "groupes": [],
                "annulee": False,
            },
            {
                "nom": "Journee sportive",
                "date": jour_passe(7),
                "lieu": "Gymnase municipal",
                "frais_inscription": 10,
                "places_disponibles": 35,
                "heure_debut": time(9, 0),
                "heure_fin": time(12, 0),
                "description": "Des jeux sportifs adaptes a chaque groupe d'age.",
                "groupes": [],
                "annulee": False,
            },
            {
                "nom": "Camp de jour thematique",
                "date": jour_futur(60),
                "lieu": "Centre de plein air",
                "frais_inscription": 35,
                "places_disponibles": 15,
                "heure_debut": time(9, 0),
                "heure_fin": time(16, 0),
                "description": "Un camp de jour sur le theme de l'aventure.",
                "groupes": [groupe_poussins],
                "annulee": True,
            },
        ]

        activites = []

        for info in donnees:
            activite, cree = Activite.objects.get_or_create(
                nom=info["nom"],
                defaults={
                    "date": info["date"],
                    "lieu": info["lieu"],
                    "frais_inscription": info["frais_inscription"],
                    "places_disponibles": info["places_disponibles"],
                    "heure_debut": info["heure_debut"],
                    "heure_fin": info["heure_fin"],
                    "description": info["description"],
                    "annulee": info["annulee"],
                },
            )

            if cree and info["groupes"]:
                activite.groupes.set(info["groupes"])

            activites.append(activite)

        return activites

    def creer_inscriptions_et_paiements(self, activites, enfants):
        enfants_par_groupe = {}

        for enfant in enfants:
            enfants_par_groupe.setdefault(enfant.groupe_id, []).append(enfant)

        for activite in activites:
            if activite.annulee:
                continue

            groupes_cibles = list(activite.groupes.all())

            if groupes_cibles:
                enfants_eligibles = [
                    enfant
                    for groupe in groupes_cibles
                    for enfant in enfants_par_groupe.get(groupe.pk, [])
                ]
            else:
                enfants_eligibles = enfants

            nombre_a_inscrire = max(len(enfants_eligibles) * 2 // 3, 1)

            for enfant in enfants_eligibles[:nombre_a_inscrire]:
                inscription, cree_inscription = InscriptionActivite.objects.get_or_create(
                    activite=activite,
                    enfant=enfant,
                )

                if activite.frais_inscription > 0 and enfant != enfants_eligibles[0]:
                    parent = enfant.parents.first()

                    if parent is not None:
                        Paiement.objects.get_or_create(
                            inscription=inscription,
                            defaults={
                                "parent": parent,
                                "montant": activite.frais_inscription,
                            },
                        )

    def creer_demandes_inscription(self, familles):
        donnees = [
            (4, "Yasmine", "Snoussi", 200, "Deuxieme enfant, cherche une place pour janvier."),
            (5, "Felix", "Roy", 900, ""),
            (10, "Ines", "Barhoumi", 1500, "Disponible immediatement."),
        ]

        for indice_famille, prenom_enfant, nom_enfant, age_jours, note in donnees:
            parent = familles[indice_famille][0]

            DemandeInscription.objects.get_or_create(
                parent=parent,
                prenom_enfant=prenom_enfant,
                nom_enfant=nom_enfant,
                defaults={
                    "date_naissance": jour_passe(age_jours),
                    "note": note,
                },
            )

    def generer_fichier_identifiants(self, administrateurs, educateurs, familles):
        chemin = Path(settings.BASE_DIR) / NOM_FICHIER_IDENTIFIANTS

        lignes = [
            "CarthageKids - Comptes de demonstration",
            "=" * 50,
            "",
            f"Mot de passe pour tous les comptes ci-dessous : {MOT_DE_PASSE_DEMO}",
            "",
            "Administrateurs",
            "-" * 50,
        ]

        for administrateur in administrateurs:
            etiquette = " (superutilisateur)" if administrateur.is_superuser else ""
            lignes.append(
                f"{administrateur.first_name} {administrateur.last_name} - "
                f"{administrateur.username}{etiquette}"
            )

        lignes += [
            "",
            "Educateurs(trices)",
            "-" * 50,
        ]

        for educateur in educateurs:
            lignes.append(f"{educateur.first_name} {educateur.last_name} - {educateur.username}")

        lignes += [
            "",
            "Parents",
            "-" * 50,
        ]

        for parents in familles:
            for parent in parents:
                lignes.append(f"{parent.first_name} {parent.last_name} - {parent.username}")

        lignes.append("")

        chemin.write_text("\n".join(lignes), encoding="utf-8")

        return chemin
