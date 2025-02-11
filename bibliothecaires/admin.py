from django.contrib import admin
from .models import Membre, Media, Livre, DVD, CD, JeuDePlateau, Emprunt

admin.site.register(Membre)
admin.site.register(Media)
admin.site.register(Livre)
admin.site.register(DVD)
admin.site.register(CD)
admin.site.register(JeuDePlateau)


class EmpruntAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "media":
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                emprunt = Emprunt.objects.get(pk=obj_id)
                kwargs["queryset"] = Media.objects.filter(disponible=True) | Media.objects.filter(pk=emprunt.media.pk)
            else:
                kwargs["queryset"] = Media.objects.filter(disponible=True)

        if db_field.name == "emprunteur":
            membres = Membre.objects.all()
            for membre in membres:
                membre.verifier_retard()

            kwargs["queryset"] = Membre.objects.filter(en_retard=False, emprunts_actifs__lt=3)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Emprunt, EmpruntAdmin)