from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from contabilidad_loslirios.models import *

class Command(BaseCommand):
    help = 'Crear grupos de usuarios y asignar permisos'

    def handle(self, *args, **options):
        # === GRUPO 1: ADMINISTRADORES ===
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        if created:
            self.stdout.write(f'✅ Grupo "Administradores" creado')
        
        # Dar TODOS los permisos a administradores
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)
        
        # === GRUPO 2: PRODUCCIÓN ===
        produccion_group, created = Group.objects.get_or_create(name='Producción')
        if created:
            self.stdout.write(f'✅ Grupo "Producción" creado')
        
        # Permisos específicos para producción
        produccion_permissions = Permission.objects.filter(
            codename__in=[
                # Jornales
                'can_view_jornales',
                'can_add_jornales',
                'can_export_jornales',
                # Riego
                'can_view_riego',
                'can_add_riego',
                # Cosecha
                'view_registrocosecha',
                'add_registrocosecha',
                # Parcelas (para el mapa)
                'view_parcela',
            ]
        )
        produccion_group.permissions.set(produccion_permissions)
        
        # === GRUPO 3: SOLO LECTURA ===
        readonly_group, created = Group.objects.get_or_create(name='Solo Lectura')
        if created:
            self.stdout.write(f'✅ Grupo "Solo Lectura" creado')
        
        # Solo permisos de visualización
        readonly_permissions = Permission.objects.filter(
            codename__in=[
                'can_view_jornales',
                'can_view_movimientos',
                'can_view_ingresos',
                'can_view_riego',
                'view_registrocosecha',
                'view_parcela',
                'can_view_analisis_data',
            ]
        )
        readonly_group.permissions.set(readonly_permissions)
        
        # === GRUPO 4: CONTABILIDAD ===
        contabilidad_group, created = Group.objects.get_or_create(name='Contabilidad')
        if created:
            self.stdout.write(f'✅ Grupo "Contabilidad" creado')
        
        # Permisos para administración financiera
        contabilidad_permissions = Permission.objects.filter(
            codename__in=[
                # Movimientos
                'can_view_movimientos',
                'can_add_movimientos',
                'can_export_movimientos',
                # Ingresos
                'can_view_ingresos',
                'can_add_ingresos',
                'can_export_ingresos',
                # Jornales (solo lectura)
                'can_view_jornales',
                'can_export_jornales',
                # Análisis
                'can_view_analisis_data',
            ]
        )
        contabilidad_group.permissions.set(contabilidad_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                '🎉 Grupos y permisos configurados exitosamente!'
            )
        )