from django.urls import path
from membres.views import MediasViews
from .views import MembresAccueilView

urlpatterns = [
    path('accueil/', MembresAccueilView.as_view(), name='accueil_membres'),
    path('medias/', MediasViews.as_view(), name='medias_membres'),
]
