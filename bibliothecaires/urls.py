from django.urls import path
from . import views

urlpatterns = [
    path('accueil/', views.BibliothecairesAccueilView.as_view(), name='accueil_bibliothecaires'),
    path('medias/', views.MediasViews.as_view(), name='medias_bibliothecaires'),
    path('medias/ajout/', views.AjoutMediaView.as_view(), name='ajout_media'),
    path('medias/ajout/livre/', views.AjoutLivreView.as_view(), name='ajout_livre'),
    path('medias/ajout/dvd/', views.AjoutDVDView.as_view(), name='ajout_dvd'),
    path('medias/ajout/cd/', views.AjoutCDView.as_view(), name='ajout_cd'),
    path('medias/ajout/jeu/', views.AjoutJeuView.as_view(), name='ajout_jeu'),
    path('medias/modification/<str:type>/<int:id>/', views.ModificationMediaView.as_view(), name='modification_media'),
    path('medias/suppression/<str:type>/<int:id>/', views.SuppressionMediaView.as_view(), name='suppression_media')
]