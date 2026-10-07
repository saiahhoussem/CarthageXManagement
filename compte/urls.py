from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "compte"

urlpatterns = [

    path("connexion/", views.connexion, name="connexion"),
    path("deconnexion/",auth_views.LogoutView.as_view(next_page="compte:connexion"), name="deconnexion"),

    path("creer_comte",views.creer_compte,name="creer_compte"),

    path("tableau-de-bord/administrateur/",views.tableau_bord_admin,name="tableau_bord_admin"),
    path("tableau-de-bord/educateur/",views.tableau_bord_educateur,name="tableau_bord_educateur"),
    path("tableau-de-bord/parent/",views.tableau_bord_parent,name="tableau_bord_parent"),

    path("educateurs/", views.liste_educateurs, name="liste_educateurs"),
    path("educateurs/<int:pk>/",views.detail_educateur, name="detail_educateur"),
    path("educateurs/<int:pk>/modifier/", views.modifier_educateur, name="modifier_educateur"),
    path("educateurs/<int:pk>/basculer/", views.basculer_statut_educateur, name="basculer_statut_educateur"),

    path("parents/", views.liste_parents, name="liste_parents"),
]
