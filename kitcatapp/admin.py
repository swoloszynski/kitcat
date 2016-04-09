from django.contrib import admin
from .models import Contact, Connection
from .models import Profile

class ConnectionInline(admin.TabularInline):
    model = Connection
    extra = 1

class ContactAdmin(admin.ModelAdmin):
    inlines = [ConnectionInline]
    fieldsets = [
        (None, {'fields': [('first_name', 'last_name', 'frequency'),
                           ('phone', 'email', 'address')]}),
        ('History', {'fields': [('date_met', 'how_met'), 'about'],
                     'classes': ['collapse']}),
    ]
    list_display = ('full_name', 'frequency', 'phone', 'email')

class ConnectionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [('contact', 'due_date', 'is_complete'), 'notes']}),
    ]
    list_display = ('contact', 'status', 'due_date')

admin.site.register(Profile)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Connection, ConnectionAdmin)
