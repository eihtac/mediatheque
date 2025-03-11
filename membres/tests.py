import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from bibliothecaires.models import Livre, DVD, CD, JeuDePlateau


@pytest.mark.django_db
class TestMedias(TestCase):
    def setUp(self):
        self.client = Client()
        self.membres_group, _ = Group.objects.get_or_create(name='membres')
        self.user = User.objects.create_user(username='Membre test', password='passwordtest')
        self.user.groups.add(self.membres_group)
        self.client.login(username='Membre test', password='passwordtest')
        self.livre = Livre.objects.create(titre='Livre test', auteur='Auteur test')
        self.dvd = DVD.objects.create(titre='DVD test', realisateur='Réalisateur test')
        self.cd = CD.objects.create(titre='CD test', artiste='Artiste test')
        self.jeu = JeuDePlateau.objects.create(nom='Jeu test', createur='Créateur test')

    def test_affichage_medias(self):
        response = self.client.get(reverse('medias_membres'))
        content = response.content.decode()
        assert response.status_code == 200
        assert 'Livre test' in content
        assert 'DVD test' in content
        assert 'CD test' in content
        assert 'Jeu test' in content