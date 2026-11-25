from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from compte import views as compte_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('comptes/', include('compte.urls')),
    path('', compte_views.accueil, name='home'),
    path('', include('enfants.urls')),
]

handler400 = "enfants.views.erreur_400"
handler403 = "enfants.views.erreur_403"
handler404 = "enfants.views.erreur_404"
handler500 = "enfants.views.erreur_500"
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
