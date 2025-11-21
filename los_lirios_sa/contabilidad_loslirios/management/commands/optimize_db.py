from django.core.management.base import BaseCommand
from django.core.cache import cache
from contabilidad_loslirios.cache import CacheManager
from contabilidad_loslirios.models import *
from django.db import transaction, connection
from django.core.management import call_command
import time

class Command(BaseCommand):
    help = 'Optimiza la base de datos y gestiona el cache de manera avanzada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--warm-cache',
            action='store_true',
            help='Pre-calentar cache con datos frecuentes',
        )
        parser.add_argument(
            '--analyze-db',
            action='store_true', 
            help='Analizar rendimiento de la base de datos',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Limpiar todo el cache',
        )
        parser.add_argument(
            '--full-optimization',
            action='store_true',
            help='Ejecutar optimización completa (recomendado)',
        )
        parser.add_argument(
            '--maintenance',
            action='store_true',
            help='Ejecutar rutinas de mantenimiento',
        )

    def handle(self, *args, **options):
        start_time = time.time()
        
        if options['clear_cache']:
            self.clear_cache()

        if options['warm_cache']:
            self.warm_cache()

        if options['analyze_db']:
            self.analyze_database()
        
        if options['maintenance']:
            self.run_maintenance()

        if options['full_optimization'] or not any(options.values()):
            # Optimización completa por defecto
            self.stdout.write('🚀 Ejecutando optimización completa...')
            self.clear_cache()
            self.warm_cache()
            self.analyze_database()
            self.run_maintenance()

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Optimización completada en {elapsed_time:.2f} segundos'
            )
        )

    def clear_cache(self):
        """Limpiar cache de manera inteligente"""
        self.stdout.write('🗑️  Limpiando cache...')
        
        # Obtener estadísticas antes de limpiar
        cache_info = self._get_cache_info()
        
        cache.clear()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Cache limpiado - {cache_info["estimated_keys"]} claves eliminadas'
            )
        )

    def warm_cache(self):
        """Pre-calentar cache de manera inteligente"""
        self.stdout.write('🔥 Pre-calentando cache...')
        
        start = time.time()
        CacheManager.warm_up_cache()
        warm_time = time.time() - start
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Cache pre-calentado en {warm_time:.2f}s'
            )
        )

    def analyze_database(self):
        """Análisis avanzado de rendimiento de base de datos"""
        self.stdout.write('📊 Analizando rendimiento de base de datos...')
        
        # Estadísticas de tablas
        tables_stats = self._get_table_statistics()
        
        self.stdout.write('\n📈 Estadísticas de tablas:')
        for table, stats in tables_stats.items():
            self.stdout.write(
                f'  {table}: {stats["count"]:,} registros, '
                f'tamaño estimado: {stats["size_mb"]:.1f}MB'
            )
        
        # Análisis de queries lentas
        self._analyze_query_performance()
        
        # Recomendaciones
        self._generate_optimization_recommendations(tables_stats)

    def run_maintenance(self):
        """Ejecutar rutinas de mantenimiento"""
        self.stdout.write('🔧 Ejecutando rutinas de mantenimiento...')
        
        # Recopilar estadísticas de base de datos
        if connection.vendor == 'postgresql':
            self._run_postgresql_maintenance()
        elif connection.vendor == 'mysql':
            self._run_mysql_maintenance()
        else:
            self.stdout.write('  Mantenimiento automático no disponible para SQLite')
        
        # Limpiar sesiones expiradas
        try:
            call_command('clearsessions', verbosity=0)
            self.stdout.write('  ✅ Sesiones expiradas limpiadas')
        except Exception as e:
            self.stdout.write(f'  ⚠️  Error limpiando sesiones: {e}')

    def _get_cache_info(self):
        """Obtener información del cache actual"""
        # Implementación básica, se puede expandir según el backend de cache
        return {
            'estimated_keys': 0,  # No hay forma estándar de contar claves en Django
            'backend': cache.__class__.__name__
        }

    def _get_table_statistics(self):
        """Obtener estadísticas detalladas de tablas"""
        stats = {}
        
        models = [
            ('MovimientoFinanciero', MovimientoFinanciero),
            ('IngresoFinanciero', IngresoFinanciero), 
            ('registro_trabajo', registro_trabajo),
            ('RegistroRiego', RegistroRiego),
            ('RegistroCosecha', RegistroCosecha),
        ]
        
        for name, model in models:
            count = model.objects.count()
            
            # Estimar tamaño (muy aproximado)
            estimated_size = count * 1000 / 1024 / 1024  # ~1KB por registro
            
            stats[name] = {
                'count': count,
                'size_mb': estimated_size
            }
        
        return stats

    def _analyze_query_performance(self):
        """Analizar performance de queries críticas"""
        self.stdout.write('\n⏱️  Analizando queries críticas:')
        
        # Queries de prueba para medir performance
        test_queries = [
            ('Dashboard KPIs', self._test_dashboard_kpis),
            ('Movimientos recientes', self._test_recent_movements),
            ('Cheques pendientes', self._test_pending_checks),
            ('Trabajadores activos', self._test_active_workers),
        ]
        
        for query_name, query_func in test_queries:
            start = time.time()
            try:
                result_count = query_func()
                query_time = (time.time() - start) * 1000
                
                status = '✅' if query_time < 100 else '⚠️' if query_time < 500 else '❌'
                self.stdout.write(
                    f'  {status} {query_name}: {query_time:.1f}ms ({result_count} resultados)'
                )
            except Exception as e:
                self.stdout.write(f'  ❌ {query_name}: Error - {e}')

    def _test_dashboard_kpis(self):
        """Test de performance para KPIs del dashboard"""
        from datetime import datetime, timedelta
        today = datetime.now().date()
        first_day = today.replace(day=1)
        
        # Simular la query del dashboard
        gastos = MovimientoFinanciero.objects.filter(
            fecha__range=[first_day, today]
        ).count()
        
        ingresos = IngresoFinanciero.objects.filter(
            fecha__range=[first_day, today]
        ).count()
        
        return gastos + ingresos

    def _test_recent_movements(self):
        """Test de performance para movimientos recientes"""
        from datetime import datetime, timedelta
        week_ago = datetime.now().date() - timedelta(days=7)
        
        return MovimientoFinanciero.objects.filter(
            fecha__gte=week_ago
        ).count()

    def _test_pending_checks(self):
        """Test de performance para cheques pendientes"""
        from datetime import datetime, timedelta
        today = datetime.now().date()
        month_ahead = today + timedelta(days=30)
        
        return IngresoFinanciero.objects.filter(
            forma_pago__in=['Cheque', 'Echeque'],
            fecha_pago__range=[today, month_ahead]
        ).count()

    def _test_active_workers(self):
        """Test de performance para trabajadores activos"""
        from datetime import datetime, timedelta
        week_ago = datetime.now().date() - timedelta(days=7)
        
        return registro_trabajo.objects.filter(
            fecha__gte=week_ago
        ).values('nombre_trabajador').distinct().count()

    def _generate_optimization_recommendations(self, tables_stats):
        """Generar recomendaciones de optimización"""
        self.stdout.write('\n💡 Recomendaciones de optimización:')
        
        total_records = sum(stats['count'] for stats in tables_stats.values())
        largest_table = max(tables_stats.items(), key=lambda x: x[1]['count'])
        
        if total_records > 50000:
            self.stdout.write('  📋 Considera implementar archivado de datos antiguos')
        
        if largest_table[1]['count'] > 10000:
            self.stdout.write(f'  🗂️  Tabla {largest_table[0]} es muy grande, optimizar consultas frecuentes')
        
        self.stdout.write('  🔄 Ejecuta este comando regularmente para mantener el rendimiento')
        self.stdout.write('  📊 Monitorea los logs para identificar consultas problemáticas')

    def _run_postgresql_maintenance(self):
        """Mantenimiento específico para PostgreSQL"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("VACUUM ANALYZE;")
                self.stdout.write('  ✅ PostgreSQL VACUUM ANALYZE ejecutado')
            except Exception as e:
                self.stdout.write(f'  ⚠️  Error en VACUUM ANALYZE: {e}')

    def _run_mysql_maintenance(self):
        """Mantenimiento específico para MySQL"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("OPTIMIZE TABLE contabilidad_loslirios_movimientofinanciero;")
                cursor.execute("OPTIMIZE TABLE contabilidad_loslirios_ingresofinanciero;")
                cursor.execute("OPTIMIZE TABLE contabilidad_loslirios_registro_trabajo;")
                self.stdout.write('  ✅ Optimización de tablas MySQL completada')
            except Exception as e:
                self.stdout.write(f'  ⚠️  Error optimizando tablas: {e}')