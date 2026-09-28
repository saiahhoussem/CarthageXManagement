from django.test import TestCase
from django.urls import reverse

from .models import User


class CreationCompteTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_test",
            password="motDePasse123",
            role=User.Role.ADMINISTRATEUR,
        )
        self.parent = User.objects.create_user(
            username="parent_test",
            password="motDePasse123",
            role=User.Role.PARENT,
        )
        self.url = reverse("utilisateurs:creer_compte")

    def test_redirige_si_non_connecte(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)

    def test_refuse_un_utilisateur_non_administrateur(self):
        self.client.login(username="parent_test", password="motDePasse123")
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)

    def test_administrateur_peut_creer_un_compte(self):
        self.client.login(username="admin_test", password="motDePasse123")
        response = self.client.post(
            self.url,
            {
                "username": "educatrice_test",
                "first_name": "Annabelle",
                "last_name": "Laundry",
                "email": "annabelle.laundry@example.com",
                "role": User.Role.EDUCATEUR,
                "telephone": "",
                "password1": "motDePasse123",
                "password2": "motDePasse123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="educatrice_test").exists())
        nouvel_utilisateur = User.objects.get(username="educatrice_test")
        self.assertEqual(nouvel_utilisateur.role, User.Role.EDUCATEUR)
        self.assertTrue(nouvel_utilisateur.check_password("motDePasse123"))

    def test_refuse_un_courriel_deja_utilise(self):
        self.client.login(username="admin_test", password="motDePasse123")
        User.objects.create_user(
            username="existant",
            email="deja.pris@example.com",
            password="motDePasse123",
            role=User.Role.PARENT,
        )
        response = self.client.post(
            self.url,
            {
                "username": "autre_utilisateur",
                "first_name": "",
                "last_name": "",
                "email": "deja.pris@example.com",
                "role": User.Role.PARENT,
                "telephone": "",
                "password1": "motDePasse123",
                "password2": "motDePasse123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="autre_utilisateur").exists())
