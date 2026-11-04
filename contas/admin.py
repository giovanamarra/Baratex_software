"""Painel administrativo: o Responsável pela instalação cadastra Gestores e as Lojas de cada um."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from contas.models import Gestor, Loja


class LojasDoGestor(admin.TabularInline):
    model = Loja
    extra = 1


@admin.register(Gestor)
class GestorAdmin(UserAdmin):
    inlines = [LojasDoGestor]


@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'gestor']
    list_filter = ['gestor']
