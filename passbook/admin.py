from django.contrib import admin
from passbook.models import Pass, Field, Location, Barcode, Signer


class PassAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'serial_number', 'organization_name',
                    'team_identifier', 'description', 'barcode')

    search_fields = ('identifier', 'serial_number', 'organization_name',
                     'team_identifier', 'description', 'barcode__message')


class FieldAdmin(admin.ModelAdmin):
    list_display = search_fields = ('key', 'label', 'value')


class BarcodeAdmin(admin.ModelAdmin):
    list_display = ('message', 'format', 'encoding', 'alt_text')
    search_fields = ('message', 'alt_text')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('longitude', 'latitude', 'altitude',
                    'relevant_text')

    search_fields = ('relevant_text',)


admin.site.register(Pass, PassAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Barcode, BarcodeAdmin)
admin.site.register(Signer)
