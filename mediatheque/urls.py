from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from membres.views import ConnexionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ConnexionView.as_view(), name='connexion'),
    path('membres/', include('membres.urls')),
    path('bibliothecaires/', include("bibliothecaires.urls")),
    path('deconnexion/', LogoutView.as_view(next_page="connexion"), name="deconnexion"),
]
