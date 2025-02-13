from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.db.models import Q
from mediatheque.forms import ConnexionForm
from bibliothecaires.models import Livre, DVD, CD, JeuDePlateau


class ConnexionView(LoginView):
    template_name = "connexion.html"
    authentication_form = ConnexionForm

    def get_success_url(self):
        if self.request.user.groups.filter(name="bibliothecaires").exists():
            return reverse_lazy('accueil_bibliothecaires')
        elif self.request.user.groups.filter(name='membres').exists():
            return reverse_lazy('accueil_membres')
        return reverse_lazy('connexion')


class MembresAccueilView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "membres/accueil.html"

    def test_func(self):
        return self.request.user.groups.filter(name='membres').exists()


class MediasViews(TemplateView):
    template_name = "membres/medias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        livres = Livre.objects.all()
        dvds = DVD.objects.all()
        cds = CD.objects.all()
        jeux = JeuDePlateau.objects.all()

        for livre in livres:
            livre.type = 'Livre'
        for dvd in dvds:
            dvd.type = 'DVD'
        for cd in cds:
            cd.type = 'CD'
        for jeu in jeux:
            jeu.type = 'Jeu'

        medias = list(livres) + list(dvds) + list(cds) + list(jeux)

        type_selectionne = self.request.GET.get("type")
        disponible_selectionne = self.request.GET.get("disponible")
        recherche = self.request.GET.get("q", "").strip().lower()

        if type_selectionne:
            medias = [media for media in medias if media.type == type_selectionne]

        if disponible_selectionne == "disponible":
            medias = [media for media in medias if hasattr(media, "disponible") and media.disponible]
        elif disponible_selectionne == "non_disponible":
            medias = [media for media in medias if (hasattr(media, "disponible") and not media.disponible) or media.type == 'Jeu']

        if recherche:
            livres = Livre.objects.filter(Q(titre__icontains=recherche) | Q(auteur__icontains=recherche))
            dvds = DVD.objects.filter(Q(titre__icontains=recherche) | Q(realisateur__icontains=recherche))
            cds = CD.objects.filter(Q(titre__icontains=recherche) | Q(artiste__icontains=recherche))
            jeux = JeuDePlateau.objects.filter(Q(nom__icontains=recherche) | Q(createur__icontains=recherche))

            for livre in livres:
                livre.type = 'Livre'
            for dvd in dvds:
                dvd.type = 'DVD'
            for cd in cds:
                cd.type = 'CD'
            for jeu in jeux:
                jeu.type = 'Jeu'

            medias = list(livres) + list(dvds) + list(cds) + list(jeux)

        context['medias'] = medias
        return context