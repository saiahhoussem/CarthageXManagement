from django.contrib import admin
from django.urls import include, path

from compte import views as compte_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('comptes/', include('compte.urls')),
    path('', compte_views.accueil, name='home'),
    path('', include('enfants.urls')),
]
