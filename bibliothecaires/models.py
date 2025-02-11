from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

class Media(models.Model):
    titre = models.CharField(max_length=250)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titre} | {'Disponible' if self.disponible else 'Ce média est déjà emprunté actuellement.'}"


class Livre(Media):
    auteur = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.titre} - Ecrit par {self.auteur} | {'Disponible' if self.disponible else 'Ce livre est déjà emprunté actuellement.'}"


class DVD(Media):
    realisateur = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.titre} - Réalisé par {self.realisateur} | {'Disponible' if self.disponible else 'Ce DVD est déjà emprunté actuellement.'}"


class CD(Media):
    artiste = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.titre} - {self.artiste} | {'Disponible' if self.disponible else 'Ce CD est déjà emprunté actuellement.'}"


class JeuDePlateau(models.Model):
    nom = models.CharField(max_length=250)
    createur = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.nom} - {self.createur} | Les jeux ne peuvent pas être empruntés."


class Membre(models.Model):
    nom = models.CharField(max_length=150)
    emprunts_actifs = models.IntegerField(default=0)
    en_retard = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        retard = "En retard." if self.en_retard else ""
        return f"{self.nom} | Emprunts actifs : {self.emprunts_actifs}. {retard}"

    def verifier_retard(self):
        self.en_retard = Emprunt.objects.filter(
            emprunteur=self,
            date_retour__lt=now().date()
        ).exists()
        self.save()

    def peut_emprunter(self):
        return not self.en_retard and self.emprunts_actifs < 3


class Emprunt(models.Model):
    emprunteur = models.ForeignKey('Membre', on_delete=models.CASCADE)
    media = models.ForeignKey('Media', on_delete=models.CASCADE)
    date_emprunt = models.DateField(auto_now_add=True)
    date_retour = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.media.titre} emprunté par {self.emprunteur.nom} le {self.date_emprunt}. Doit être rendu le {self.date_retour}."

    def save(self, *args, **kwargs):
        if self.pk:
            emprunt_existant = Emprunt.objects.get(pk=self.pk)

            if emprunt_existant.emprunteur != self.emprunteur:
                emprunt_existant.emprunteur.emprunts_actifs -= 1
                emprunt_existant.emprunteur.save()
                self.emprunteur.emprunts_actifs += 1

            if emprunt_existant.media != self.media:
                emprunt_existant.media.disponible = True
                emprunt_existant.media.save()
                self.media.disponible = False

        else:
            self.emprunteur.emprunts_actifs += 1
            self.media.disponible = False

        if not self.date_retour:
            self.date_retour = now().date() + timedelta(days=7)

        super().save(*args, **kwargs)
        self.emprunteur.verifier_retard()
        self.emprunteur.save()
        self.media.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.emprunteur.emprunts_actifs -= 1
        self.media.disponible = True
        self.emprunteur.verifier_retard()
        self.emprunteur.save()
        self.media.save()

@receiver(post_save, sender=Membre)
def creer_utilisateur_membre(sender, instance, created, **kwargs):
    if created and not instance.user:
        user = User.objects.create_user(username=instance.nom, password="password")
        Membre.objects.filter(pk=instance.pk).update(user=user)
        membres_group = Group.objects.get(name="membres")
        user.groups.add(membres_group)
