# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	cpf = models.CharField(max_length=13, blank = True)
	idUfsc = models.CharField(max_length=50, blank = True)
	setor = models.CharField(max_length=20, blank = True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

class Unidade(models.Model):
	sigla = models.CharField(max_length=10, unique=True)
	nome = models.TextField()
	unidadePai = models.ForeignKey('self', blank=True, null=True, default=1)
	responsavel = models.ForeignKey(User)
	descricao = models.TextField()
	logo = models.FileField(blank=True)

	def __unicode__(self):
		return self.sigla
	def __str__(self):
		return self.sigla

class Atividade(models.Model):
	nome = models.CharField(max_length=30)
	descricao = models.TextField()

	def __unicode__(self):
		return self.nome
	def __str__(self):
		return self.nome

class Locavel(models.Model):
	class Meta:
		abstract = True

	nome = models.TextField()
	descricao = models.TextField()
	responsavel = models.ForeignKey(User)
	unidade = models.ForeignKey(Unidade)
	bloqueado = models.BooleanField(default=False)
	visivel = models.BooleanField(default=True)
	localizacao = models.TextField()
	foto = models.FileField(blank=True)
	def __unicode__(self):
		return self.nome
	def __str__(self):
		return self.nome

class EspacoFisico(Locavel):
	capacidade = models.PositiveSmallIntegerField()
	atividadesPermitidas = models.ManyToManyField(Atividade)

class Equipamento(Locavel):
	patrimonio = models.PositiveIntegerField()

class Reserva(models.Model):
	class Meta:
		abstract = True
	
	estados = (('A','Aprovado'),('D','Desaprovado'),('E','Esperando'))
	estado = models.CharField(max_length=1, choices=estados, default='E')
	data = models.DateField()
	horaInicio = models.TimeField()
	horaFim = models.TimeField()
	dataReserva  = models.DateTimeField(auto_now_add=True)
	atividade = models.ForeignKey(Atividade)
	usuario = models.ForeignKey(User)
	ramal = models.PositiveIntegerField()
	finalidade = models.TextField()
	
	def __unicode__(self):
		return self.usuario.username+"/"+self.atividade.nome

class ReservaEspacoFisico(Reserva):
	espacoFisico = models.ForeignKey(EspacoFisico)


class ReservaEquipamento(Reserva):
	espacoFisico = models.ForeignKey(Equipamento)

