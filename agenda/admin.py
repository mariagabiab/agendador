from django.contrib import admin
from agenda.models import *
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.contrib.admin.sites import AdminSite
import forms

admin.site.register(Atividade)

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">account_balance</i>'
    form = forms.UnidadeAdminForm

    def get_form(self, request, obj=None, **kwargs):
        AdminForm =  super(UnidadeAdmin, self).get_form(request, obj, **kwargs)
        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest

    def search_children(self, units, unit):
        children = Unidade.objects.filter(unidadePai=unit)
        for child in children:
            if child.nome == unit.nome:
                children = children.exclude(nome=unit.nome)
        if children:
            for child in children:
                units = self.search_children(units, child)
        else:
            unit = Unidade.objects.filter(id=unit.id)
            units = units | unit
            return units
        unit = Unidade.objects.filter(id=unit.id)
        units = units | unit
        return units

    def get_queryset(self, request):
        qs = super(UnidadeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        units = Unidade.objects.none()
        unit_responsible = Unidade.objects.filter(responsavel=request.user)
        for unit in unit_responsible:
            units = self.search_children(units, unit)
        units = units.distinct()
        return units

    def get_readonly_fields(self, request, obj=None):
        qs = super(UnidadeAdmin, self).get_queryset(request)
        qsResp = qs.filter(responsavel=request.user)
        if request.user.is_superuser:
            return []
        if obj in qsResp:
            return ['responsavel']
        return []

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'locavel', 'data', 'ramal', 'finalidade', 'estado')
    search_fields = ['finalidade', 'usuario__username']

    def get_queryset(self, request, reserveModel, reservableModel):
        if request.user.is_superuser:
            return reserveModel.objects.all()

        reserves = reserveModel.objects.none()
        #Check if unit responsible
        unit_responsible = Unidade.objects.filter(responsavel=request.user)
        if unit_responsible:
            reservable = reservableModel.objects.filter(unidade=unit_responsible)
            reserves = reserves | reserveModel.objects.filter(locavel=reservable)
            #Check for children unit
            for unit in unit_responsible:
                reserves = self.search_children(reserves, unit, reserveModel, reservableModel)
#               item = Equipamento.objects.filter(unidade=child)
#               for item_child in item:
#                   reserves = reserves | item_child.reservalocavel_set.all()
        #Check if reservable responsible
        reservable_responsible = reservableModel.objects.filter(responsavel=request.user)
        if reservable_responsible:
            for reservable in reservable_responsible:
                reserves = reserves | reserveModel.objects.filter(locavel=reservable)

        #Add own reserves
        reserves = reserves | reserveModel.objects.filter(usuario=request.user)

        reserves = reserves.distinct()
        return reserves

    def search_children(self, reserves, unit, reserveModel, reservableModel):
        children = Unidade.objects.filter(unidadePai=unit)
        for child in children:
            if child.nome == unit.nome:
                children = children.exclude(nome=unit.nome)
        if children:
            for child in children:
                reserves = self.search_children(reserves, child, reserveModel, reservableModel)
        else:
            reservables = reservableModel.objects.filter(unidade = unit)
            for reservable in reservables:
                reserves = reserves | reserveModel.objects.filter(locavel=reservable)
            return reserves
        reservables = reservableModel.objects.filter(unidade=unit)
        for reservable in reservables:
            reserves = reserves | reserveModel.objects.filter(locavel=reservable)
        return reserves

class ReservaEquipamentoAdmin(ReservaAdmin):
    form = forms.ReservaEquipamentoAdminForm
    icon = '<i class="material-icons">power</i>'

    def get_form(self, request, obj=None, **kwargs):
        AdminForm =  super(ReservaEquipamentoAdmin, self).get_form(request, obj, **kwargs)
        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest

    def get_queryset(self, request):
        return super(ReservaEquipamentoAdmin, self).get_queryset(request, ReservaEquipamento, Equipamento)

admin.site.register(ReservaEquipamento, ReservaEquipamentoAdmin)

class ReservaEspacoFisicoAdmin(ReservaAdmin):
    form = forms.ReservaEspacoFisicoAdminForm
    icon = '<i class="material-icons">room</i>'

    def get_form(self, request, obj=None, **kwargs):
        AdminForm =  super(ReservaEspacoFisicoAdmin, self).get_form(request, obj, **kwargs)
        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest

    def get_queryset(self, request):
        return super(ReservaEspacoFisicoAdmin, self).get_queryset(request, ReservaEspacoFisico, EspacoFisico)

admin.site.register(ReservaEspacoFisico, ReservaEspacoFisicoAdmin)

class LocavelAdmin(admin.ModelAdmin):
    list_display = ('nome','unidade','get_responsavel')
    def get_responsavel(self, obj):
        return ", ".join(responsavel.username for responsavel in obj.responsavel.all())
    get_responsavel.short_description = 'responsavel'

    def add_reservable(self, user, unit, reservable, reservables, responsable, reservableModel):
        # Check if reservable belongs to a specific group, if so it's ignored
        group = reservable.grupos.all()
        if not group and unit not in user.unidade_set.all() and not responsable:
            reservables = reservables | reservableModel.objects.filter(id=reservable.id).exclude(invisivel=True)
        elif unit in user.unidade_set.all() or responsable:
            reservables = reservables | reservableModel.objects.filter(id=reservable.id)
        return reservables
    
    def search_children(self, reservables, unit, user, responsable, reservableModel):
        children = Unidade.objects.filter(unidadePai=unit)
        for child in children:
            if child.nome == unit.nome:
                children = children.exclude(nome=unit.nome)
        if children:
            for child in children:
                if not child.grupos.all() or responsable:
                    reservables = self.search_children(reservables, child, user, responsable, reservableModel)
        else:
            child_reservables = reservableModel.objects.filter(unidade=unit)
            ## Test if equipment isn't bound to a specific group
            for reservable in child_reservables:
                reservables = self.add_reservable(user, unit, reservable, reservables, responsable, reservableModel)
            return reservables
        # You may also have a son AND equipments, this equipment may also belong to a group
        unit_reservables = reservableModel.objects.filter(unidade=unit)
        for reservable in unit_reservables:
            reservables = self.add_reservable(user, unit, reservable, reservables, responsable, reservableModel)
        return reservables

    def get_queryset(self, request, reservableModel, group_reservables):
        if request.user.is_superuser:
            return reservableModel.objects.all()
        reservables = reservableModel.objects.none()
        # Check if unit responsible
        # Also check user unit via group, for form list purposes
        groups = request.user.groups.all()
        group_units = Unidade.objects.none()
        for group in groups:
            if group.unidade_set:
                group_units = group_units | group.unidade_set.all()
        if group_units:
            for unit in group_units:
                reservables = self.search_children(reservables, unit, request.user, False, reservableModel)

        unit_responsible = Unidade.objects.filter(responsavel=request.user)
        if unit_responsible:
            for unit in unit_responsible:
                reservables = self.search_children(reservables, unit, request.user, True, reservableModel)

        # Get all locables user's responsible
        reservables = reservables | reservableModel.objects.filter(responsavel=request.user)
        # Unit via group already tested, now test group exclusive spaces
        # This can't be done in this parent method since there's a need to know which set from group to pick,
        # that's why it's an argument
        reservables = reservables | group_reservables
        reservables = reservables.distinct()
        return reservables

class EquipamentoAdmin(LocavelAdmin):

    def get_queryset(self, request):
        groups = request.user.groups.all()
        group_reservables = Equipamento.objects.none()
        for group in groups:
            group_reservables = group_reservables | group.equipamento_set.all()
        return super(EquipamentoAdmin, self).get_queryset(request, Equipamento, group_reservables)

admin.site.register(Equipamento, EquipamentoAdmin)

class EspacoFisicoAdmin(LocavelAdmin):

    def get_queryset(self, request):
        groups = request.user.groups.all()
        group_reservables = EspacoFisico.objects.none()
        for group in groups:
            group_reservables = group_reservables | group.espacofisico_set.all()
        return super(EspacoFisicoAdmin, self).get_queryset(request, EspacoFisico, group_reservables)

admin.site.register(EspacoFisico, EspacoFisicoAdmin)