from django.urls import path
from .views import BibliothecairesAccueilView

urlpatterns = [
    path('accueil/', BibliothecairesAccueilView.as_view(), name='accueil_bibliothecaires')
]