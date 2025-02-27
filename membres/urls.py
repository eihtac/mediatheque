from django.urls import path
from . import views

urlpatterns = [
    path('accueil/', views.MembresAccueilView.as_view(), name='accueil_membres'),
    path('medias/', views.MediasViews.as_view(), name='medias_membres'),
]
