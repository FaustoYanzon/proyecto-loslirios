"""
Custom test runners y utilidades para testing
"""

from django.test.runner import DiscoverRunner
from django.test import TestCase, TransactionTestCase
from django.core.management import call_command
from django.db import connection
from django.core.cache import cache
import time
import sys

class FastTestRunner(DiscoverRunner):
    """
    Test runner optimizado para velocidad
    """
    
    def setup_test_environment(self, **kwargs):
        """Configurar entorno de test optimizado"""
        super().setup_test_environment(**kwargs)
        
        # Configuraciones para velocidad
        from django.conf import settings
        settings.DEBUG = False
        settings.LOGGING_CONFIG = None
        
        # Deshabilitar migraciones innecesarias
        settings.MIGRATION_MODULES = {
            'contabilidad_loslirios': None,
            'auth': None,
            'contenttypes': None,
            'sessions': None,
            'messages': None,
            'staticfiles': None,
        }

    def setup_databases(self, **kwargs):
        """Configurar bases de datos para test"""
        result = super().setup_databases(**kwargs)
        
        # Crear índices necesarios para performance
        with connection.cursor() as cursor:
            # Índices para queries frecuentes en tests
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS test_movimiento_fecha 
                ON contabilidad_loslirios_movimientofinanciero(fecha)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS test_ingreso_fecha 
                ON contabilidad_loslirios_ingresofinanciero(fecha)
            """)
        
        return result

    def teardown_databases(self, old_config, **kwargs):
        """Limpiar después de tests"""
        # Limpiar cache
        cache.clear()
        super().teardown_databases(old_config, **kwargs)


class BaseTestCase(TestCase):
    """
    Clase base para tests con utilidades comunes
    """
    
    @classmethod
    def setUpClass(cls):
        """Setup a nivel de clase"""
        super().setUpClass()
        cls.start_time = time.time()

    @classmethod
    def tearDownClass(cls):
        """Cleanup a nivel de clase"""
        end_time = time.time()
        duration = end_time - cls.start_time
        if duration > 5:  # Más de 5 segundos
            print(f"⚠️  Test class {cls.__name__} tardó {duration:.2f}s")
        super().tearDownClass()

    def setUp(self):
        """Setup común para todos los tests"""
        super().setUp()
        cache.clear()
        self.test_start = time.time()

    def tearDown(self):
        """Cleanup común para todos los tests"""
        test_duration = time.time() - self.test_start
        if test_duration > 1:  # Más de 1 segundo
            print(f"⚠️  Test {self._testMethodName} tardó {test_duration:.2f}s")
        super().tearDown()

    def assertResponseTimeUnder(self, response_time, max_time):
        """Assert personalizado para tiempo de respuesta"""
        self.assertLess(
            response_time, max_time,
            f"Response time {response_time:.3f}s excede el máximo {max_time}s"
        )

    def create_test_user(self, username='testuser', password='testpass123'):
        """Crear usuario de prueba estándar"""
        from django.contrib.auth.models import User
        return User.objects.create_user(
            username=username,
            password=password,
            email=f'{username}@test.com'
        )

    def create_test_movimiento(self, **kwargs):
        """Crear movimiento de prueba con datos por defecto"""
        from contabilidad_loslirios.models import MovimientoFinanciero
        from decimal import Decimal
        from datetime import date
        
        defaults = {
            'fecha': date.today(),
            'origen': 'Test Origen',
            'finca': 'Los Lirios',
            'tipo': 'Gasto',
            'clasificacion': 'Cosecha',
            'detalle': 'Test detalle',
            'monto': Decimal('100.00'),
            'moneda': 'USD',
            'forma_pago': 'Efectivo'
        }
        defaults.update(kwargs)
        return MovimientoFinanciero.objects.create(**defaults)

    def create_test_ingreso(self, **kwargs):
        """Crear ingreso de prueba con datos por defecto"""
        from contabilidad_loslirios.models import IngresoFinanciero
        from decimal import Decimal
        from datetime import date
        
        defaults = {
            'fecha': date.today(),
            'origen': 'Venta Test',
            'destino': 'Cliente Test',
            'comprador': 'Comprador Test',
            'forma_pago': 'Efectivo',
            'monto': Decimal('1000.00'),
            'moneda': 'USD'
        }
        defaults.update(kwargs)
        return IngresoFinanciero.objects.create(**defaults)


class PerformanceTestCase(BaseTestCase):
    """
    Clase base para tests de performance
    """
    
    def measure_time(self, func, max_time=1.0):
        """Medir tiempo de ejecución de una función"""
        start_time = time.time()
        result = func()
        end_time = time.time()
        
        duration = end_time - start_time
        self.assertResponseTimeUnder(duration, max_time)
        
        return result, duration

    def create_bulk_test_data(self, count=100):
        """Crear datos de prueba en bulk para tests de performance"""
        from contabilidad_loslirios.models import MovimientoFinanciero
        from decimal import Decimal
        from datetime import date, timedelta
        
        movimientos = []
        for i in range(count):
            movimientos.append(MovimientoFinanciero(
                fecha=date.today() - timedelta(days=i % 30),
                origen=f'Origen {i}',
                finca='Los Lirios',
                tipo='Gasto',
                clasificacion='Cosecha',
                detalle=f'Detalle {i}',
                monto=Decimal(f'{i + 10}.00'),
                moneda='USD',
                forma_pago='Efectivo'
            ))
        
        MovimientoFinanciero.objects.bulk_create(movimientos)
        return count


class IntegrationTestCase(TransactionTestCase):
    """
    Clase base para tests de integración que necesitan transacciones
    """
    
    def setUp(self):
        """Setup para tests de integración"""
        super().setUp()
        cache.clear()
        
        # Cargar fixtures si son necesarias
        # call_command('loaddata', 'test_fixtures.json')

    def simulate_user_flow(self, user_actions):
        """Simular flujo de usuario completo"""
        from django.test import Client
        
        client = Client()
        results = []
        
        for action in user_actions:
            method = action.get('method', 'GET')
            url = action['url']
            data = action.get('data', {})
            
            if method == 'POST':
                response = client.post(url, data)
            else:
                response = client.get(url, data)
            
            results.append({
                'action': action,
                'response': response,
                'status_code': response.status_code
            })
        
        return results