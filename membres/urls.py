from django.urls import path
from .views import MembresAccueilView

urlpatterns = [
    path('accueil/', MembresAccueilView.as_view(), name='accueil_membres')
]
