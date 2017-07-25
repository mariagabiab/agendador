from django.contrib import admin
from agenda.models import *
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False
	verbose_name_plural = 'Profile'
	fk_name = 'user'

class CustomUserAdmin(UserAdmin):
	inlines = (ProfileInline, )

	def get_inline_instances(self, request, obj=None):
		if not obj:
			return list()
		return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Atividade)
#admin.site.register(EspacoFisico)
#admin.site.register(Equipamento)

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
	icon = '<i class="material-icons">group</i>'

	def get_queryset(self, request):
		qs = super(UnidadeAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(responsavel=request.user)

	def get_readonly_fields(self, request, obj=None):
		qs = super(UnidadeAdmin, self).get_queryset(request)
		qsResp = qs.filter(responsavel=request.user)
		if request.user.is_superuser:
			return []
		if obj in qsResp:
			return ['responsavel']
		return []

class ReservaEquipamentoAdmin(admin.ModelAdmin):
	list_display = ('usuario', 'espacoFisico', 'data', 'ramal', 'finalidade')
	search_fields = ['finalidade', 'usuario__username']
	icon = '<i class="material-icons">power</i>'

admin.site.register(ReservaEquipamento, ReservaEquipamentoAdmin)

class ReservaEspacoFisicoAdmin(admin.ModelAdmin):
	list_display = ('usuario', 'espacoFisico', 'data', 'ramal', 'finalidade')
	search_fields = ['finalidade', 'usuario__username']
	icon = '<i class="material-icons">room</i>'
admin.site.register(ReservaEspacoFisico, ReservaEspacoFisicoAdmin)

class EquipamentoAdmin(admin.ModelAdmin):
	list_display = ('nome','unidade','responsavel')

	def get_queryset(self, request):
		qs = super(EquipamentoAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(responsavel=request.user)

	def get_readonly_fields(self, request, obj=None):
		qs = super(EquipamentoAdmin, self).get_queryset(request)
		qsResp = qs.filter(responsavel=request.user)
		if request.user.is_superuser:
			return []
		if obj in qsResp:
			return ['responsavel', 'unidade']
		return []

admin.site.register(Equipamento, EquipamentoAdmin)

class EspacoFisicoAdmin(admin.ModelAdmin):
	list_display = ('nome','unidade','responsavel')

	def get_queryset(self, request):
		qs = super(EspacoFisicoAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(responsavel=request.user)

	def get_readonly_fields(self, request, obj=None):
		qs = super(EspacoFisicoAdmin, self).get_queryset(request)
		qsResp = qs.filter(responsavel=request.user)
		if request.user.is_superuser:
			return []
		if obj in qsResp:
			return ['responsavel', 'unidade']
		return []

admin.site.register(EspacoFisico, EspacoFisicoAdmin)	