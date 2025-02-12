from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView


class BibliothecairesAccueilView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "bibliothecaires/accueil.html"

    def test_func(self):
        return self.request.user.groups.filter(name='bibliothecaires').exists()