from django.contrib import admin
from models import *
# Register your models here.

admin.site.register(Departamento)
admin.site.register(EspacoFisico)
admin.site.register(TipoEvento)
admin.site.register(Usuario)
admin.site.register(Reserva)
admin.site.register(Entry, EntryAdmin)
