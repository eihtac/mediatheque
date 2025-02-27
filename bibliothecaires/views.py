from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Livre, DVD, CD, JeuDePlateau


class BibliothecairesAccueilView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "bibliothecaires/accueil.html"

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()


class MediasViews(TemplateView):
    template_name = "bibliothecaires/medias.html"

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


class AjoutMediaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'bibliothecaires/ajout_media.html'

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()

    def get(self, request, *args, **kwargs):
        type_media = request.GET.get('type_media')

        if type_media in ['livre', 'dvd', 'cd', 'jeu']:
            return redirect(reverse_lazy(f'ajout_{type_media}'))
        return render(request, self.template_name)


class AjoutLivreView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'bibliothecaires/ajout_livre.html'

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()

    def post(self, request, *args, **kwargs):
        titre = request.POST.get('titre')
        auteur = request.POST.get('auteur')

        if titre and auteur:
            Livre.objects.create(titre=titre, auteur=auteur)
            return redirect(reverse_lazy('medias_bibliothecaires'))


class AjoutDVDView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'bibliothecaires/ajout_dvd.html'

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()

    def post(self, request, *args, **kwargs):
        titre = request.POST.get('titre')
        realisateur = request.POST.get('realisateur')

        if titre and realisateur:
            DVD.objects.create(titre=titre, realisateur=realisateur)
            return redirect(reverse_lazy('medias_bibliothecaires'))


class AjoutCDView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'bibliothecaires/ajout_cd.html'

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()

    def post(self, request, *args, **kwargs):
        titre = request.POST.get('titre')
        artiste = request.POST.get('artiste')

        if titre and artiste:
            CD.objects.create(titre=titre, artiste=artiste)
            return redirect(reverse_lazy('medias_bibliothecaires'))


class AjoutJeuView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'bibliothecaires/ajout_jeu.html'

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()

    def post(self, request, *args, **kwargs):
        nom = request.POST.get('nom')
        createur = request.POST.get('createur')

        if nom and createur:
            JeuDePlateau.objects.create(nom=nom, createur=createur)
            return redirect(reverse_lazy('medias_bibliothecaires'))


class ModificationMediaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "bibliothecaires/modification_media.html"

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()

    def get(self, request, type, id, *args, **kwargs):
        if type == 'livre':
            media = get_object_or_404(Livre, id=id)
        elif type == 'dvd':
            media = get_object_or_404(DVD, id=id)
        elif type == 'cd':
            media = get_object_or_404(CD, id=id)
        elif type == 'jeu':
            media = get_object_or_404(JeuDePlateau, id=id)

        return render(request, self.template_name, {'media': media, 'type': type})

    def post(self, request, type, id, *args, **kwargs):
        if type == 'livre':
            media = get_object_or_404(Livre, id=id)
            media.titre = request.POST.get('titre')
            media.auteur = request.POST.get('auteur')
        elif type == 'dvd':
            media = get_object_or_404(DVD, id=id)
            media.titre = request.POST.get('titre')
            media.realisateur = request.POST.get('realisateur')
        elif type == 'cd':
            media = get_object_or_404(CD, id=id)
            media.titre = request.POST.get('titre')
            media.artiste = request.POST.get('artiste')
        elif type == 'jeu':
            media = get_object_or_404(JeuDePlateau, id=id)
            media.nom = request.POST.get('nom')
            media.createur = request.POST.get('createur')

        media.save()
        return redirect(reverse_lazy('medias_bibliothecaires'))


class SuppressionMediaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'bibliothecaires/suppression_media.html'

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()

    def get(self, request, type, id, *args, **kwargs):
        if type == 'livre':
            media = get_object_or_404(Livre, id=id)
        elif type == 'dvd':
            media = get_object_or_404(DVD, id=id)
        elif type == 'cd':
            media = get_object_or_404(CD, id=id)
        elif type == 'jeu':
            media = get_object_or_404(JeuDePlateau, id=id)

        return render(request, self.template_name, {'media': media})

    def post(self, request, type, id, *args, **kwargs):
        if type == 'livre':
            media = get_object_or_404(Livre, id=id)
        elif type == 'dvd':
            media = get_object_or_404(DVD, id=id)
        elif type == 'cd':
            media = get_object_or_404(CD, id=id)
        elif type == 'jeu':
            media = get_object_or_404(JeuDePlateau, id=id)

        media.delete()
        return redirect(reverse_lazy('medias_bibliothecaires'))