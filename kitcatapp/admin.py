from django.contrib import admin
from .models import Contact, Connection

class ContactAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [('first_name', 'last_name', 'frequency'),
                           ('phone', 'email', 'address')]}),
        ('History', {'fields': [('date_met', 'how_met'), 'about'],
                     'classes': ['collapse']}),
    ]

admin.site.register(Contact, ContactAdmin)
admin.site.register(Connection)
