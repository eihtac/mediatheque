import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.models import Group, User
from datetime import timedelta
from .models import Livre, DVD, CD, JeuDePlateau, Membre, Emprunt


@pytest.mark.django_db
class TestMedias(TestCase):
    def setUp(self):
        self.client = Client()
        self.bibliothecaires_group, _ = Group.objects.get_or_create(name='bibliothecaires')
        self.bibliothecaire_user = User.objects.create_user(username='Bibliothecaire Test', password='passwordtest')
        self.bibliothecaire_user.groups.add(self.bibliothecaires_group)
        self.client.login(username='Bibliothecaire Test', password='passwordtest')
        self.livre = Livre.objects.create(titre='Livre test', auteur='Auteur test')
        self.dvd = DVD.objects.create(titre='DVD test', realisateur='Réalisateur test')
        self.cd = CD.objects.create(titre='CD test', artiste='Artiste test')
        self.jeu = JeuDePlateau.objects.create(nom='Jeu test', createur='Créateur test')

    def test_affichage_medias(self):
        response = self.client.get(reverse('medias_bibliothecaires'))
        content = response.content.decode()
        assert response.status_code == 200
        assert 'Livre test' in content
        assert 'DVD test' in content
        assert 'CD test' in content
        assert 'Jeu test' in content

    def test_acces_bibliothecaire(self):
        response = self.client.get(reverse('ajout_media'))
        assert response.status_code == 200

    def test_acces_non_bibliothecaire(self):
        self.client.logout()
        response = self.client.get(reverse('ajout_media'))
        assert response.status_code == 302

    def test_ajout_media(self):
        response = self.client.post(reverse('ajout_livre'), {'titre':'Nouveau Livre', 'auteur':'Auteur test'})
        assert Livre.objects.filter(titre='Nouveau Livre').exists()


@pytest.mark.django_db
class TestMembres(TestCase):
    def setUp(self):
        self.client = Client()
        self.membres_group, _ = Group.objects.get_or_create(name='membres')
        self.bibliothecaires_group, _ = Group.objects.get_or_create(name='bibliothecaires')
        self.user = User.objects.create_user(username='User test', password='passwordtest')
        self.user.groups.add(self.bibliothecaires_group)
        self.client.login(username='User test', password='passwordtest')
        self.membre = Membre.objects.create(nom='Membre test')

    def test_affichage_membres(self):
        response = self.client.get(reverse('membres'))
        content = response.content.decode()
        assert response.status_code == 200
        assert 'Membre test' in content

    def test_ajout_membre(self):
        response = self.client.post(reverse('ajout_membre'), {'nom': 'Nouveau membre'})
        assert Membre.objects.filter(nom='Nouveau membre').exists()

    def test_modification_membre(self):
        response = self.client.post(reverse('modification_membre', args=[self.membre.id]), {'nom': 'Nouveau nom'})
        self.membre.refresh_from_db()
        assert self.membre.nom == 'Nouveau nom'

    def test_suppression_membre(self):
        response = self.client.post(reverse('suppression_membre', args=[self.membre.id]))
        assert not Membre.objects.filter(id=self.membre.id).exists()

    def test_membre_peut_emprunter(self):
        assert self.membre.peut_emprunter() is True

    def test_membre_en_retard(self):
        media = Livre.objects.create(titre='Livre test', auteur='Auteur test')
        Emprunt.objects.create(emprunteur=self.membre, media=media, date_retour=now().date() - timedelta(days=5))
        self.membre.verifier_retard()
        self.membre.refresh_from_db()
        assert self.membre.en_retard is True
        assert self.membre.peut_emprunter() is False

    def test_membre_limite_emprunt(self):
        for i in range(3):
            media = Livre.objects.create(titre=f"Livre test {i}", auteur='Auteur test')
            Emprunt.objects.create(emprunteur=self.membre, media=media)

        self.membre.refresh_from_db()
        assert self.membre.peut_emprunter() is False


@pytest.mark.django_db
class TestEmprunts(TestCase):
    def setUp(self):
        self.client = Client()
        self.groupe_membres, _ = Group.objects.get_or_create(name='membres')
        self.groupe_bibliothecaires, _ = Group.objects.get_or_create(name='bibliothecaires')
        self.user = User.objects.create_user(username='User test', password='passwordtest')
        self.user.groups.add(self.groupe_bibliothecaires)
        self.client.login(username='User test', password='passwordtest')
        self.membre = Membre.objects.create(nom='Membre test')
        self.media = Livre.objects.create(titre='Livre test', auteur='Auteur test')
        self.emprunt = Emprunt.objects.create(emprunteur=self.membre, media=self.media)

    def test_affichage_emprunts(self):
        response = self.client.get(reverse('emprunts'))
        content = response.content.decode()
        assert response.status_code == 200
        assert str(self.emprunt.id) in content

    def test_ajout_emprunt(self):
        nouveau_media = Livre.objects.create(titre='Nouveau Livre', auteur='Auteur test')
        response = self.client.post(reverse('ajout_emprunt'), {'membre': self.membre.id, 'media': nouveau_media.id})
        assert Emprunt.objects.filter(emprunteur=self.membre, media=nouveau_media).exists()
        self.membre.refresh_from_db()
        nouveau_media.refresh_from_db()
        assert self.membre.emprunts_actifs == 2
        assert nouveau_media.disponible is False

    def test_suppression_emprunt(self):
        response = self.client.post(reverse('retour_emprunt', args=[self.emprunt.id]))
        assert not Emprunt.objects.filter(id=self.emprunt.id).exists()
        self.membre.refresh_from_db()
        self.media.refresh_from_db()
        assert self.membre.emprunts_actifs == 0
        assert self.media.disponible is True

    def test_emprunt_en_retard(self):
        self.emprunt.date_retour = now().date() - timedelta(days=5)
        self.emprunt.save()
        self.membre.verifier_retard()
        assert self.membre.en_retard is True