from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.admin.sites import AdminSite

from .models import *
from .admin import *

class MockRequest:
    pass
request = MockRequest()

class AdminViewPermissionsTests(TestCase):

    def create_preset(self):
        # Create users with different prioritys
        # Also gives them all permissions and staff so they can see admin page
        permissions = Permission.objects.all()
        common = User.objects.create_user('common', password='a')
        common.is_staff=True
        common.user_permissions.set(permissions)
        common.save()
        item_responsable = User.objects.create_user('item_responsable', password='a')
        item_responsable.is_staff=True
        item_responsable.user_permissions.set(permissions)
        item_responsable.save()
        sub_unit_responsable = User.objects.create_user('sub_unit_responsable', password='a')
        sub_unit_responsable.is_staff=True
        sub_unit_responsable.user_permissions.set(permissions)
        sub_unit_responsable.save()
        unit_responsable = User.objects.create_user('unit_responsable', password='a')
        unit_responsable.is_staff=True
        unit_responsable.user_permissions.set(permissions)
        unit_responsable.save()
        superuser = User.objects.create_user('superuser', password='a')
        superuser.is_superuser=True
        superuser.is_staff=True
        superuser.save()

        # Create units to their respective responsable
        parentUnit = Unidade.objects.create(sigla='pu', nome='parent unit', responsavel=unit_responsable, descricao='test')
        parentUnit.save()
        childUnit = Unidade.objects.create(sigla='cu', nome='child unit', responsavel=sub_unit_responsable, unidadePai=parentUnit, descricao='test')
        parentUnit.save()

        # Create a room and a equipment for each user (except common)
        room0 = EspacoFisico.objects.create(nome='room0', descricao='test', responsavel=item_responsable, unidade=childUnit, capacidade=0)
        room0.save()
        equipment0 = Equipamento.objects.create(nome='equipment0', descricao='test', responsavel=item_responsable, unidade=childUnit, patrimonio=0)
        equipment0.save()
        room1 = EspacoFisico.objects.create(nome='room1', descricao='test', responsavel=sub_unit_responsable, unidade=childUnit, capacidade=0)
        room1.save()
        equipment1 = Equipamento.objects.create(nome='equipment1', descricao='test', responsavel=sub_unit_responsable, unidade=childUnit, patrimonio=0)
        equipment1.save()
        room2 = EspacoFisico.objects.create(nome='room2', descricao='test', responsavel=unit_responsable, unidade=parentUnit, capacidade=0)
        room2.save()
        equipment2 = Equipamento.objects.create(nome='equipment2', descricao='test', responsavel=unit_responsable, unidade=parentUnit, patrimonio=0)
        equipment2.save()

        # Create a activitie (required for reserve)
        activitie = Atividade.objects.create(nome='activitie', descricao='default')

        # Create a reserve for both room and equipment for each user
        reserve_room0 = ReservaEspacoFisico.objects.create(data='1000-10-10', horaInicio='00:00', horaFim='00:00', atividade=activitie, usuario=common, ramal=0, finalidade='t', espacoFisico=room0)
        reserve_room0.save()
        reserve_equipment0 = ReservaEquipamento.objects.create(data='1000-10-10', horaInicio='00:00', horaFim='00:00', atividade=activitie, usuario=common, ramal=0, finalidade='t', equipamento=equipment0)
        reserve_equipment0.save()
        reserve_room1 = ReservaEspacoFisico.objects.create(data='1000-10-10', horaInicio='00:00', horaFim='00:00', atividade=activitie, usuario=item_responsable, ramal=0, finalidade='t', espacoFisico=room1)
        reserve_room1.save()
        reserve_equipment1 = ReservaEquipamento.objects.create(data='1000-10-10', horaInicio='00:00', horaFim='00:00', atividade=activitie, usuario=item_responsable, ramal=0, finalidade='t', equipamento=equipment1)
        reserve_equipment1.save()
        reserve_room2 = ReservaEspacoFisico.objects.create(data='1000-10-10', horaInicio='00:00', horaFim='00:00', atividade=activitie, usuario=sub_unit_responsable, ramal=0, finalidade='t', espacoFisico=room2)
        reserve_room2.save()
        reserve_equipment2 = ReservaEquipamento.objects.create(data='1000-10-10', horaInicio='00:00', horaFim='00:00', atividade=activitie, usuario=sub_unit_responsable, ramal=0, finalidade='t', equipamento=equipment2)
        reserve_equipment2.save()

        return {'rooms': [room0, room1, room2],
                'equipments': [equipment0, equipment1, equipment2],
                'room_reserves': [reserve_room0, reserve_room1, reserve_room2],
                'equipment_reserves': [reserve_equipment0, reserve_equipment1, reserve_equipment2]}

    def check_items(self, user, items, room=True, equipment=True):
        request.user = user
        if room:
            ma = EspacoFisicoAdmin(EspacoFisico, AdminSite())
            rooms = list(ma.get_queryset(request))
            self.assertItemsEqual(rooms, items['rooms'])
        if equipment:
            ma = EquipamentoAdmin(Equipamento, AdminSite())
            equipments = list(ma.get_queryset(request))
            self.assertItemsEqual(equipments, items['equipments'])
        ma  = ReservaEspacoFisicoAdmin(ReservaEspacoFisico, AdminSite())
        room_reserves = list(ma.get_queryset(request))
        self.assertItemsEqual(room_reserves, items['room_reserves'])
        ma = ReservaEquipamentoAdmin(ReservaEquipamento, AdminSite())
        equipment_reserves = list(ma.get_queryset(request))
        self.assertItemsEqual(equipment_reserves, items['equipment_reserves'])

    def test_admin_view_filter(self):
        print 'TESTING ADMIN VIEW FILTER'
        items = self.create_preset()

        # First superuser, he must see everything in items
        user = User.objects.get(username='superuser')
        self.check_items(user, items)
        print '-SUPERUSER CASE PASS'

        # Unit_responsable also must see every item, even though he's not responsable for reserves
        user = User.objects.get(username='unit_responsable')
        self.check_items(user, items)
        print '-UNIT RESPONSABLE CASE PASS'

        # Sub_unit_responsable must be able to see everything but room and equipment 2
        user = User.objects.get(username='sub_unit_responsable')
        request.user = user
        ma = EspacoFisicoAdmin(EspacoFisico, AdminSite())
        rooms = list(ma.get_queryset(request))
        self.assertEqual(2, len(rooms))
        temp = list(items['rooms'])
        temp.pop()
        self.assertItemsEqual(temp, rooms)
        ma = EquipamentoAdmin(Equipamento, AdminSite())
        equipments = list(ma.get_queryset(request))
        self.assertEqual(2, len(equipments))
        temp = list(items['equipments'])
        temp.pop()
        self.assertItemsEqual(temp, equipments)
        self.check_items(user, items, room=False, equipment=False)
        print '-SUB UNIT RESPONSABLE CASE PASS'

        # Item responsable can only see rooms and equipments 0 and reserves 0 and 1
        user = User.objects.get(username='item_responsable')
        request.user = user
        ma = EspacoFisicoAdmin(EspacoFisico, AdminSite())
        rooms = list(ma.get_queryset(request))
        self.assertEqual(1, len(rooms))
        temp = list(items['rooms'])
        temp.pop()
        temp.pop()
        self.assertItemsEqual(temp, rooms)
        ma = EquipamentoAdmin(Equipamento, AdminSite())
        equipments = list(ma.get_queryset(request))
        self.assertEqual(1, len(equipments))
        temp = list(items['equipments'])
        temp.pop()
        temp.pop()
        self.assertItemsEqual(temp, equipments)
        ma = ReservaEspacoFisicoAdmin(ReservaEspacoFisico, AdminSite())
        room_reserves = list(ma.get_queryset(request))
        self.assertEqual(2, len(room_reserves))
        temp = list(items['room_reserves'])
        temp.pop()
        self.assertItemsEqual(temp, room_reserves)
        ma = ReservaEquipamentoAdmin(ReservaEquipamento, AdminSite())
        equipment_reserves = list(ma.get_queryset(request))
        self.assertEqual(2, len(equipment_reserves))
        temp = list(items['equipment_reserves'])
        temp.pop()
        self.assertItemsEqual(temp, equipment_reserves)
        print '-ITEM RESPONSABLE CASE PASS'

        # Common user can only see reserves 0
        user = User.objects.get(username='common')
        request.user = user
        ma = EspacoFisicoAdmin(EspacoFisico,AdminSite())
        rooms = list(ma.get_queryset(request))
        self.assertEqual(0, len(rooms))
        ma = EquipamentoAdmin(Equipamento, AdminSite())
        equipments = list(ma.get_queryset(request))
        self.assertEqual(0, len(equipments))
        ma = ReservaEquipamentoAdmin(ReservaEquipamento, AdminSite())
        equipment_reserves = list(ma.get_queryset(request))
        self.assertEqual(1, len(equipment_reserves))
        temp = list(items['equipment_reserves'])
        temp.pop()
        temp.pop()
        self.assertItemsEqual(temp, equipment_reserves)
        ma = ReservaEspacoFisicoAdmin(ReservaEspacoFisico, AdminSite())
        room_reserves = list(ma.get_queryset(request))
        self.assertEqual(1, len(room_reserves))
        temp = list(items['room_reserves'])
        temp.pop()
        temp.pop()
        self.assertItemsEqual(temp, room_reserves)
        print '-COMMON USER CASE PASS'