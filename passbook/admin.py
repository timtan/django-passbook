from django.contrib import admin
from passbook.models import Pass, Field, Location, Barcode, Signer


class PassAdmin(admin.ModelAdmin):
    pass

admin.site.register(Pass, PassAdmin)
admin.site.register(Field)
admin.site.register(Location)
admin.site.register(Barcode)
admin.site.register(Signer)
