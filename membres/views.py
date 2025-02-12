from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from mediatheque.forms import ConnexionForm


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