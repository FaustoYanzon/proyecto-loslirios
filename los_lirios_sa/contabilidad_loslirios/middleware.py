from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
import time
import logging
import sys
import gc

# Configurar logger
logger = logging.getLogger('contabilidad_loslirios')

class CacheInvalidationMiddleware(MiddlewareMixin):
    """Middleware para invalidar cache automáticamente cuando hay cambios"""
    
    def process_request(self, request):
        """Marcar el inicio del request para medir tiempo de respuesta"""
        request._cache_start_time = time.time()
        if settings.DEBUG:
            from django.db import connection
            request._queries_before = len(connection.queries)
        return None

    def process_response(self, request, response):
        """Invalidar cache si hay cambios en datos y medir rendimiento"""
        
        # Medir tiempo de respuesta
        if hasattr(request, '_cache_start_time'):
            response_time = time.time() - request._cache_start_time
            
            queries_executed = 0
            if settings.DEBUG and hasattr(request, '_queries_before'):
                from django.db import connection
                queries_executed = len(connection.queries) - request._queries_before
            
            # Headers de debugging para desarrollo
            if settings.DEBUG:
                response['X-Response-Time'] = f"{response_time:.3f}s"
                response['X-DB-Queries'] = str(queries_executed)
            
            # Log queries lentas
            if response_time > 1.0:
                logger.warning(
                    f"Query lenta detectada: {request.path} - {response_time:.2f}s "
                    f"({queries_executed} queries)"
                )
        
        # Invalidar cache en operaciones de escritura exitosas
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if response.status_code in [200, 201, 204]:
                self._invalidate_relevant_cache(request)
        
        return response

    def _invalidate_relevant_cache(self, request):
        """Invalidar cache relevante según la URL"""
        path = request.path.lower()
        
        try:
            # Importar aquí para evitar errores de importación circular
            from .cache import CacheManager
            
            if any(keyword in path for keyword in ['movimiento', 'gasto', 'egreso']):
                CacheManager.invalidate_dashboard_cache()
                CacheManager.invalidate_form_options_cache('MovimientoFinanciero')
                logger.info(f"Cache invalidado: MovimientoFinanciero en {request.path}")
                
            elif any(keyword in path for keyword in ['ingreso', 'cheque']):
                CacheManager.invalidate_dashboard_cache()
                CacheManager.invalidate_form_options_cache('IngresoFinanciero')
                logger.info(f"Cache invalidado: IngresoFinanciero en {request.path}")
                
            elif any(keyword in path for keyword in ['jornal', 'trabajo', 'trabajador']):
                CacheManager.invalidate_dashboard_cache()
                CacheManager.invalidate_form_options_cache('registro_trabajo')
                logger.info(f"Cache invalidado: registro_trabajo en {request.path}")
                
            elif any(keyword in path for keyword in ['cosecha']):
                CacheManager.invalidate_dashboard_cache()
                CacheManager.invalidate_form_options_cache('RegistroCosecha')
                logger.info(f"Cache invalidado: RegistroCosecha en {request.path}")
                
            elif any(keyword in path for keyword in ['riego']):
                CacheManager.invalidate_dashboard_cache()
                logger.info(f"Cache invalidado: RegistroRiego en {request.path}")
                
        except Exception as e:
            logger.error(f"Error al invalidar cache: {e}")

class DatabaseOptimizationMiddleware(MiddlewareMixin):
    """Middleware para optimización de consultas de base de datos"""
    
    def process_request(self, request):
        """Preparar optimizaciones por request"""
        return None
    
    def process_response(self, request, response):
        """Monitorear y optimizar consultas"""
        
        if settings.DEBUG and hasattr(request, '_queries_before'):
            try:
                from django.db import connection
                queries_executed = len(connection.queries) - request._queries_before
                
                # Alertar sobre muchas queries
                if queries_executed > 15:
                    logger.warning(
                        f"Alto número de queries: {queries_executed} en {request.path}"
                    )
                    
                    # Log las queries más lentas (solo en desarrollo)
                    if hasattr(connection, 'queries') and queries_executed > 0:
                        recent_queries = connection.queries[-queries_executed:]
                        slow_queries = [
                            q for q in recent_queries
                            if q.get('time') and float(q.get('time', 0)) > 0.1
                        ]
                        
                        if slow_queries:
                            logger.warning(f"Queries lentas encontradas: {len(slow_queries)}")
                            for i, query in enumerate(slow_queries[:3]):  # Solo las 3 más lentas
                                sql_preview = query['sql'][:100].replace('\n', ' ')
                                logger.warning(f"Query lenta #{i+1} ({query['time']}s): {sql_preview}...")
                                
            except Exception as e:
                logger.error(f"Error en monitoreo de DB: {e}")
        
        return response

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware para monitoreo de rendimiento básico (sin dependencias externas)"""
    
    def process_request(self, request):
        """Iniciar monitoreo de performance"""
        request._perf_start = time.time()
        request._memory_before = self._get_memory_usage()
        return None
    
    def process_response(self, request, response):
        """Registrar métricas de performance"""
        
        if hasattr(request, '_perf_start'):
            duration = time.time() - request._perf_start
            memory_after = self._get_memory_usage()
            memory_delta = memory_after - getattr(request, '_memory_before', 0)
            
            # Registrar métricas críticas
            if duration > 2.0:  # Requests muy lentos
                logger.error(
                    f"Request crítico: {request.path} - "
                    f"{duration:.2f}s, memoria: {memory_delta:.1f}KB"
                )
            elif duration > 1.0:  # Requests lentos
                logger.warning(
                    f"Request lento: {request.path} - {duration:.2f}s"
                )
            
            # Headers para debugging (solo en desarrollo)
            if settings.DEBUG:
                response['X-Memory-Delta'] = f"{memory_delta:.1f}KB"
                response['X-Performance-Score'] = self._calculate_performance_score(duration)
        
        return response
    
    def _get_memory_usage(self):
        """Obtener uso básico de memoria usando sys (sin dependencias externas)"""
        try:
            # Método alternativo usando sys y gc (incorporados en Python)
            import sys
            import gc
            
            # Forzar garbage collection para medición más precisa
            gc.collect()
            
            # Obtener tamaño de todos los objetos en memoria
            total_size = sum(sys.getsizeof(obj) for obj in gc.get_objects())
            return total_size / 1024  # KB
            
        except Exception as e:
            # Si hay error, retornar 0 para que no rompa la aplicación
            logger.debug(f"No se pudo medir memoria: {e}")
            return 0
    
    def _calculate_performance_score(self, duration):
        """Calcular score de performance (A-F)"""
        if duration < 0.1:
            return 'A'
        elif duration < 0.3:
            return 'B'
        elif duration < 0.7:
            return 'C'
        elif duration < 1.5:
            return 'D'
        else:
            return 'F'

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware simple para logging de requests importantes"""
    
    def process_request(self, request):
        """Log requests importantes"""
        if any(keyword in request.path for keyword in ['/api/', '/admin/', 'cargar_', 'consultar_']):
            logger.info(f"Request: {request.method} {request.path} - Usuario: {getattr(request.user, 'username', 'Anonymous')}")
        return None
    
    def process_response(self, request, response):
        """Log responses con errores"""
        if response.status_code >= 400:
            logger.error(f"Error {response.status_code}: {request.method} {request.path}")
        return response