from django.core.cache import cache
from django.db.models import Sum, Count, Q
from .models import MovimientoFinanciero, IngresoFinanciero, registro_trabajo, RegistroCosecha, RegistroRiego
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger('contabilidad_loslirios')

class CacheManager:
    """Gestor centralizado de cache para optimizar consultas frecuentes"""
    
    # Tiempos de cache en segundos
    CACHE_TIMES = {
        'dashboard_kpis': 300,  # 5 minutos
        'monthly_stats': 1800,  # 30 minutos  
        'yearly_stats': 3600,   # 1 hora
        'form_options': 7200,   # 2 horas
        'heavy_queries': 900,   # 15 minutos
        'user_data': 1200,      # 20 minutos
    }

    @classmethod
    def get_cache_key(cls, prefix, *args):
        """Generar clave de cache consistente"""
        key_parts = [str(arg) for arg in args if arg is not None]
        return f"los_lirios_{prefix}_{'_'.join(key_parts)}"

    @classmethod
    def get_dashboard_kpis(cls, fecha_desde, fecha_hasta):
        """Cache para KPIs del dashboard con datos más completos"""
        cache_key = cls.get_cache_key('dashboard_kpis', fecha_desde, fecha_hasta)
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT para dashboard KPIs: {cache_key}")
            return cached_data
        
        logger.info(f"Cache MISS para dashboard KPIs: {cache_key}")
        
        # Calcular KPIs frescos con queries optimizadas
        gastos_mes = MovimientoFinanciero.objects.filter(
            fecha__range=[fecha_desde, fecha_hasta]
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        ingresos_mes = IngresoFinanciero.objects.filter(
            fecha__range=[fecha_desde, fecha_hasta]
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        # Trabajadores únicos del período
        trabajadores_mes = registro_trabajo.objects.filter(
            fecha__range=[fecha_desde, fecha_hasta]
        ).values('nombre_trabajador').distinct().count()
        
        # Cheques y echeques del período
        cheques_data = IngresoFinanciero.objects.filter(
            fecha__range=[fecha_desde, fecha_hasta],
            forma_pago__in=['Cheque', 'Echeque']
        ).aggregate(
            count=Count('id_ingreso'),
            total=Sum('monto')
        )
        
        # Cosecha del período
        cosecha_data = RegistroCosecha.objects.filter(
            fecha__range=[fecha_desde, fecha_hasta]
        ).aggregate(
            registros=Count('id'),
            kg_totales=Sum('kg_totales')
        )
        
        # Riego del período
        riego_data = RegistroRiego.objects.filter(
            inicio__date__range=[fecha_desde, fecha_hasta]
        ).count()
        
        data = {
            'gastos_mes': float(gastos_mes),
            'ingresos_mes': float(ingresos_mes),
            'saldo_disponible': float(ingresos_mes - gastos_mes),
            'trabajadores_mes': trabajadores_mes,
            'cheques_count': cheques_data['count'] or 0,
            'cheques_monto': float(cheques_data['total'] or 0),
            'cosecha_registros': cosecha_data['registros'] or 0,
            'cosecha_kg': float(cosecha_data['kg_totales'] or 0),
            'riego_registros': riego_data,
            'timestamp': datetime.now().isoformat(),
            'periodo': f"{fecha_desde}_to_{fecha_hasta}"
        }
        
        cache.set(cache_key, data, cls.CACHE_TIMES['dashboard_kpis'])
        logger.info(f"Cache SET para dashboard KPIs: {cache_key}")
        return data

    @classmethod  
    def get_form_options(cls, model_name, field_name):
        """Cache para opciones de formularios dinámicos con más campos"""
        cache_key = cls.get_cache_key('form_options', model_name, field_name)
        cached_options = cache.get(cache_key)
        
        if cached_options is not None:
            logger.info(f"Cache HIT para opciones: {cache_key}")
            return cached_options
        
        logger.info(f"Cache MISS para opciones: {cache_key}")
        
        # Obtener opciones frescas según el modelo
        try:
            if model_name == 'MovimientoFinanciero':
                if field_name == 'clasificacion':
                    options = list(MovimientoFinanciero.objects.values_list('clasificacion', flat=True).distinct())
                elif field_name == 'tipo':
                    options = list(MovimientoFinanciero.objects.values_list('tipo', flat=True).distinct())
                elif field_name == 'origen':
                    options = list(MovimientoFinanciero.objects.values_list('origen', flat=True).distinct())
                else:
                    options = []
            elif model_name == 'IngresoFinanciero':
                if field_name == 'comprador':
                    options = list(IngresoFinanciero.objects.values_list('comprador', flat=True).distinct())
                elif field_name == 'destino':
                    options = list(IngresoFinanciero.objects.values_list('destino', flat=True).distinct())
                elif field_name == 'forma_pago':
                    options = list(IngresoFinanciero.objects.values_list('forma_pago', flat=True).distinct())
                else:
                    options = []
            elif model_name == 'registro_trabajo':
                if field_name == 'nombre_trabajador':
                    options = list(registro_trabajo.objects.values_list('nombre_trabajador', flat=True).distinct())
                elif field_name == 'ubicacion':
                    options = list(registro_trabajo.objects.values_list('ubicacion', flat=True).distinct())
                elif field_name == 'tarea':
                    options = list(registro_trabajo.objects.values_list('tarea', flat=True).distinct())
                else:
                    options = []
            elif model_name == 'RegistroCosecha':
                if field_name == 'finca':
                    options = list(RegistroCosecha.objects.values_list('finca', flat=True).distinct())
                elif field_name == 'variedad':
                    options = list(RegistroCosecha.objects.values_list('variedad', flat=True).distinct())
                elif field_name == 'comprador':
                    options = list(RegistroCosecha.objects.values_list('comprador', flat=True).distinct())
                else:
                    options = []
            else:
                options = []
        except Exception as e:
            logger.error(f"Error obteniendo opciones para {model_name}.{field_name}: {e}")
            options = []
        
        # Limpiar y ordenar opciones
        options = sorted([opt for opt in options if opt and opt.strip()])
        
        cache.set(cache_key, options, cls.CACHE_TIMES['form_options'])
        logger.info(f"Cache SET para opciones: {cache_key} - {len(options)} items")
        return options

    @classmethod
    def get_monthly_summary(cls, year, month):
        """Cache para resúmenes mensuales completos"""
        cache_key = cls.get_cache_key('monthly_summary', year, month)
        cached_summary = cache.get(cache_key)
        
        if cached_summary is not None:
            logger.info(f"Cache HIT para resumen mensual: {cache_key}")
            return cached_summary
        
        logger.info(f"Cache MISS para resumen mensual: {cache_key}")
        
        # Calcular resumen mensual
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Queries optimizadas con agregaciones
        gastos_data = MovimientoFinanciero.objects.filter(
            fecha__range=[start_date, end_date]
        ).aggregate(
            total=Sum('monto'),
            count=Count('id_movimiento')
        )
        
        ingresos_data = IngresoFinanciero.objects.filter(
            fecha__range=[start_date, end_date]
        ).aggregate(
            total=Sum('monto'),
            count=Count('id_ingreso')
        )
        
        trabajo_data = registro_trabajo.objects.filter(
            fecha__range=[start_date, end_date]
        ).aggregate(
            trabajadores=Count('nombre_trabajador', distinct=True),
            registros=Count('id_registro'),
            monto_total=Sum('monto_total')
        )
        
        cosecha_data = RegistroCosecha.objects.filter(
            fecha__range=[start_date, end_date]
        ).aggregate(
            registros=Count('id'),
            kg_totales=Sum('kg_totales')
        )
        
        summary = {
            'periodo': f"{year}-{month:02d}",
            'gastos': {
                'total': float(gastos_data['total'] or 0),
                'registros': gastos_data['count'] or 0
            },
            'ingresos': {
                'total': float(ingresos_data['total'] or 0),
                'registros': ingresos_data['count'] or 0
            },
            'trabajo': {
                'trabajadores_activos': trabajo_data['trabajadores'] or 0,
                'registros': trabajo_data['registros'] or 0,
                'monto_total': float(trabajo_data['monto_total'] or 0)
            },
            'cosecha': {
                'registros': cosecha_data['registros'] or 0,
                'kg_totales': float(cosecha_data['kg_totales'] or 0)
            },
            'saldo': float((ingresos_data['total'] or 0) - (gastos_data['total'] or 0)),
            'timestamp': datetime.now().isoformat()
        }
        
        cache.set(cache_key, summary, cls.CACHE_TIMES['monthly_stats'])
        logger.info(f"Cache SET para resumen mensual: {cache_key}")
        return summary

    @classmethod
    def get_cheques_pendientes(cls):
        """Cache específico para cheques pendientes (usado en dashboard)"""
        cache_key = cls.get_cache_key('cheques_pendientes')
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT para cheques pendientes")
            return cached_data
        
        logger.info(f"Cache MISS para cheques pendientes")
        
        # Cheques próximos a vencer (30 días)
        hoy = datetime.now().date()
        fecha_limite = hoy + timedelta(days=30)
        
        cheques = IngresoFinanciero.objects.filter(
            forma_pago__in=['Cheque', 'Echeque'],
            fecha_pago__isnull=False,
            fecha_pago__gte=hoy,
            fecha_pago__lte=fecha_limite
        ).select_related().only(
            'id_ingreso', 'comprador', 'fecha_pago', 'monto', 
            'numero_cheque', 'banco', 'forma_pago'
        ).order_by('fecha_pago')
        
        # Convertir a diccionarios para serialización
        cheques_data = [{
            'id': cheque.id_ingreso,
            'comprador': cheque.comprador,
            'fecha_pago': cheque.fecha_pago.isoformat(),
            'monto': float(cheque.monto),
            'numero_cheque': cheque.numero_cheque,
            'banco': cheque.banco,
            'forma_pago': cheque.forma_pago,
        } for cheque in cheques]
        
        summary = {
            'cheques': cheques_data,
            'total_cheques': len(cheques_data),
            'monto_total': sum(c['monto'] for c in cheques_data),
            'timestamp': datetime.now().isoformat()
        }
        
        cache.set(cache_key, summary, cls.CACHE_TIMES['dashboard_kpis'])
        logger.info(f"Cache SET para cheques pendientes: {len(cheques_data)} cheques")
        return summary

    @classmethod
    def invalidate_dashboard_cache(cls):
        """Invalidar cache del dashboard cuando hay nuevos datos"""
        today = datetime.now().date()
        
        # Invalidar varios períodos
        periods = [
            # Mes actual
            (today.replace(day=1), today),
            # Últimos 7 días
            (today - timedelta(days=7), today),
            # Últimos 30 días
            (today - timedelta(days=30), today)
        ]
        
        for start, end in periods:
            cache_key = cls.get_cache_key('dashboard_kpis', start, end)
            cache.delete(cache_key)
        
        # Invalidar cheques pendientes
        cache.delete(cls.get_cache_key('cheques_pendientes'))
        
        # Invalidar resumen mensual actual
        cache.delete(cls.get_cache_key('monthly_summary', today.year, today.month))
        
        logger.info("Cache del dashboard invalidado")

    @classmethod  
    def invalidate_form_options_cache(cls, model_name, field_name=None):
        """Invalidar cache de opciones de formularios"""
        if field_name:
            cache_key = cls.get_cache_key('form_options', model_name, field_name)
            cache.delete(cache_key)
        else:
            # Invalidar todas las opciones del modelo
            common_fields = {
                'MovimientoFinanciero': ['clasificacion', 'tipo', 'origen'],
                'IngresoFinanciero': ['comprador', 'destino', 'forma_pago'],
                'registro_trabajo': ['nombre_trabajador', 'ubicacion', 'tarea'],
                'RegistroCosecha': ['finca', 'variedad', 'comprador']
            }
            
            for field in common_fields.get(model_name, []):
                cache_key = cls.get_cache_key('form_options', model_name, field)
                cache.delete(cache_key)
        
        logger.info(f"Cache de opciones invalidado para {model_name}.{field_name or 'all'}")

    @classmethod
    def warm_up_cache(cls):
        """Pre-calentar cache con datos frecuentemente consultados"""
        today = datetime.now().date()
        
        # Pre-cargar KPIs del mes actual
        first_day_month = today.replace(day=1)
        cls.get_dashboard_kpis(first_day_month, today)
        
        # Pre-cargar KPIs de últimos 30 días
        cls.get_dashboard_kpis(today - timedelta(days=30), today)
        
        # Pre-cargar cheques pendientes
        cls.get_cheques_pendientes()
        
        # Pre-cargar opciones de formularios más comunes
        common_options = [
            ('MovimientoFinanciero', 'clasificacion'),
            ('MovimientoFinanciero', 'tipo'),
            ('IngresoFinanciero', 'comprador'),
            ('IngresoFinanciero', 'destino'),
            ('registro_trabajo', 'nombre_trabajador'),
            ('registro_trabajo', 'ubicacion'),
            ('RegistroCosecha', 'finca'),
            ('RegistroCosecha', 'variedad'),
        ]
        
        for model_name, field_name in common_options:
            cls.get_form_options(model_name, field_name)
        
        # Pre-cargar resumen mensual
        cls.get_monthly_summary(today.year, today.month)
        
        logger.info(f"Cache pre-calentado para {today.strftime('%B %Y')}")

    @classmethod
    def get_cache_stats(cls):
        """Obtener estadísticas del cache para monitoreo"""
        stats = {
            'cache_keys_checked': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Esta función sería expandida en una implementación real
        # con contadores más específicos
        return stats