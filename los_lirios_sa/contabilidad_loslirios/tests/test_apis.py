from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
import json
from datetime import date, timedelta
from decimal import Decimal
from contabilidad_loslirios.models import MovimientoFinanciero, IngresoFinanciero, registro_trabajo
from unittest.mock import patch
import time

class DashboardKPIsAPITestCase(TestCase):
    """Tests específicos para la API de KPIs del dashboard"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Limpiar cache antes de cada test
        cache.clear()

    def test_kpis_api_structure(self):
        """Test: Estructura correcta de respuesta de API"""
        response = self.client.get(reverse('dashboard_kpis_api'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        
        # Campos requeridos en la respuesta
        required_fields = [
            'gasto_total_mes', 'ingresos_mes', 'saldo_disponible',
            'cheques_mes', 'monto_cheques_mes', 'trabajadores_mes',
            'variacion_gastos', 'variacion_ingresos',
            'sparkline_gastos', 'sparkline_ingresos',
            'tiene_datos', 'success', 'timestamp'
        ]
        
        for field in required_fields:
            self.assertIn(field, data, f"Campo {field} faltante en respuesta")

    def test_kpis_api_with_data(self):
        """Test: API con datos reales"""
        # Crear datos de prueba
        MovimientoFinanciero.objects.create(
            fecha=date.today(),
            origen='Test Gasto',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Cosecha',
            detalle='Test',
            monto=Decimal('300.00'),
            moneda='USD',
            forma_pago='Efectivo'
        )
        
        IngresoFinanciero.objects.create(
            fecha=date.today(),
            origen='Test Ingreso',
            destino='Cliente',
            comprador='Test Client',
            forma_pago='Efectivo',
            monto=Decimal('1500.00'),
            moneda='USD'
        )
        
        registro_trabajo.objects.create(
            fecha=date.today(),
            nombre_trabajador='Juan Test',
            clasificacion='Cosecha',
            tarea='Corte',
            detalle='Test',
            cantidad=Decimal('8.0'),
            unidad_medida='Horas',
            precio=Decimal('15.00'),
            ubicacion='Test'
        )
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        data = json.loads(response.content)
        
        # Verificar cálculos
        self.assertEqual(float(data['gasto_total_mes']), 300.00)
        self.assertEqual(float(data['ingresos_mes']), 1500.00)
        self.assertEqual(float(data['saldo_disponible']), 1200.00)  # 1500 - 300
        self.assertEqual(data['trabajadores_mes'], 1)
        self.assertTrue(data['tiene_datos'])
        self.assertTrue(data['success'])

    def test_kpis_api_without_data(self):
        """Test: API sin datos"""
        response = self.client.get(reverse('dashboard_kpis_api'))
        data = json.loads(response.content)
        
        self.assertEqual(float(data['gasto_total_mes']), 0.0)
        self.assertEqual(float(data['ingresos_mes']), 0.0)
        self.assertEqual(float(data['saldo_disponible']), 0.0)
        self.assertEqual(data['trabajadores_mes'], 0)
        self.assertFalse(data['tiene_datos'])

    def test_kpis_api_sparklines(self):
        """Test: Sparklines contienen datos de últimos 7 días"""
        # Crear datos para diferentes días
        for i in range(7):
            fecha = date.today() - timedelta(days=i)
            MovimientoFinanciero.objects.create(
                fecha=fecha,
                origen=f'Gasto día {i}',
                finca='Los Lirios',
                tipo='Gasto',
                clasificacion='Cosecha',
                detalle='Test',
                monto=Decimal(f'{(i+1)*10}.00'),
                moneda='USD',
                forma_pago='Efectivo'
            )
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        data = json.loads(response.content)
        
        # Sparklines deben tener 7 puntos
        self.assertEqual(len(data['sparkline_gastos']), 7)
        self.assertEqual(len(data['sparkline_ingresos']), 7)
        
        # Debe haber datos en sparkline_gastos
        self.assertGreater(sum(data['sparkline_gastos']), 0)

    def test_kpis_api_variaciones(self):
        """Test: Cálculo de variaciones mes anterior"""
        # Datos mes actual
        MovimientoFinanciero.objects.create(
            fecha=date.today(),
            origen='Gasto actual',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Cosecha',
            detalle='Test',
            monto=Decimal('200.00'),
            moneda='USD',
            forma_pago='Efectivo'
        )
        
        # Datos mes anterior
        mes_anterior = date.today() - timedelta(days=35)
        MovimientoFinanciero.objects.create(
            fecha=mes_anterior,
            origen='Gasto anterior',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Cosecha',
            detalle='Test',
            monto=Decimal('100.00'),
            moneda='USD',
            forma_pago='Efectivo'
        )
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        data = json.loads(response.content)
        
        # Variación debería ser 100% (200 vs 100)
        self.assertAlmostEqual(float(data['variacion_gastos']), 100.0, places=1)

    def test_kpis_api_cheques_calculation(self):
        """Test: Cálculo específico de cheques"""
        # Ingreso efectivo
        IngresoFinanciero.objects.create(
            fecha=date.today(),
            origen='Efectivo',
            destino='Cliente',
            comprador='Cliente Efectivo',
            forma_pago='Efectivo',
            monto=Decimal('1000.00'),
            moneda='USD'
        )
        
        # Ingreso cheque
        IngresoFinanciero.objects.create(
            fecha=date.today(),
            origen='Cheque',
            destino='Cliente',
            comprador='Cliente Cheque',
            forma_pago='Cheque',
            monto=Decimal('500.00'),
            moneda='USD'
        )
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        data = json.loads(response.content)
        
        self.assertEqual(data['cheques_mes'], 1)
        self.assertEqual(float(data['monto_cheques_mes']), 500.00)

    @patch('contabilidad_loslirios.cache.CacheManager.get_dashboard_kpis')
    def test_kpis_api_cache_behavior(self, mock_cache):
        """Test: Comportamiento del cache en API"""
        # Simular cache hit
        mock_cache.return_value = {
            'gastos_mes': 100.0,
            'ingresos_mes': 500.0,
            'saldo_disponible': 400.0,
            'trabajadores_mes': 2,
            'timestamp': '2024-01-01T00:00:00'
        }
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        data = json.loads(response.content)
        
        # Verificar que usa datos del cache
        self.assertEqual(float(data['gasto_total_mes']), 100.0)
        self.assertEqual(float(data['ingresos_mes']), 500.0)
        mock_cache.assert_called_once()

    def test_kpis_api_performance(self):
        """Test: Performance de la API"""
        # Crear muchos datos para probar performance
        for i in range(50):
            MovimientoFinanciero.objects.create(
                fecha=date.today() - timedelta(days=i % 30),
                origen=f'Gasto {i}',
                finca='Los Lirios',
                tipo='Gasto',
                clasificacion='Cosecha',
                detalle=f'Test {i}',
                monto=Decimal(f'{i + 10}.00'),
                moneda='USD',
                forma_pago='Efectivo'
            )
        
        start_time = time.time()
        response = self.client.get(reverse('dashboard_kpis_api'))
        end_time = time.time()
        
        # Debe responder en menos de 1 segundo
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(response.status_code, 200)

    def test_kpis_api_error_handling(self):
        """Test: Manejo de errores en API"""
        # Simular error desconectando la base de datos temporalmente
        # (Este test es más conceptual, en producción usarías mocks)
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        data = json.loads(response.content)
        
        # La API debe responder con estructura consistente incluso con errores
        self.assertIn('success', data)
        self.assertIn('timestamp', data)


class AutocompletarAPITestCase(TestCase):
    """Tests para APIs de autocompletar"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Crear datos para autocompletar
        MovimientoFinanciero.objects.create(
            fecha=date.today(),
            origen='Ferretería Central',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Cosecha',
            detalle='Test',
            monto=Decimal('100.00'),
            moneda='USD',
            forma_pago='Efectivo'
        )
        
        MovimientoFinanciero.objects.create(
            fecha=date.today(),
            origen='Ferretería Norte',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Insumos',
            detalle='Test',
            monto=Decimal('150.00'),
            moneda='USD',
            forma_pago='Efectivo'
        )

    def test_autocompletar_origen_movimiento(self):
        """Test: Autocompletar origen de movimientos"""
        response = self.client.get(
            reverse('autocompletar_origen_movimiento'), 
            {'term': 'Ferr'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        
        # Debe retornar lista de sugerencias
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Verificar estructura de respuesta
        for item in data:
            self.assertIn('value', item)
            self.assertIn('label', item)
        
        # Verificar que incluye las ferreterías
        origenes = [item['value'] for item in data]
        self.assertIn('Ferretería Central', origenes)
        self.assertIn('Ferretería Norte', origenes)

    def test_autocompletar_sin_resultados(self):
        """Test: Autocompletar sin resultados"""
        response = self.client.get(
            reverse('autocompletar_origen_movimiento'), 
            {'term': 'NoExiste'}
        )
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

    def test_autocompletar_term_vacio(self):
        """Test: Autocompletar con término vacío"""
        response = self.client.get(
            reverse('autocompletar_origen_movimiento'), 
            {'term': ''}
        )
        
        data = json.loads(response.content)
        # Con término vacío, no debe retornar resultados
        self.assertEqual(len(data), 0)

    def test_autocompletar_case_insensitive(self):
        """Test: Autocompletar es case insensitive"""
        response = self.client.get(
            reverse('autocompletar_origen_movimiento'), 
            {'term': 'ferr'}  # minúsculas
        )
        
        data = json.loads(response.content)
        self.assertGreater(len(data), 0)


class CacheAPITestCase(TestCase):
    """Tests para comportamiento del cache en APIs"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        cache.clear()

    def test_cache_invalidation_on_post(self):
        """Test: Cache se invalida al crear nuevos datos"""
        # Cargar datos en cache
        response1 = self.client.get(reverse('dashboard_kpis_api'))
        data1 = json.loads(response1.content)
        
        # Crear nuevo movimiento
        MovimientoFinanciero.objects.create(
            fecha=date.today(),
            origen='Nuevo Gasto',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Cosecha',
            detalle='Test cache',
            monto=Decimal('250.00'),
            moneda='USD',
            forma_pago='Efectivo'
        )
        
        # Cargar datos nuevamente
        response2 = self.client.get(reverse('dashboard_kpis_api'))
        data2 = json.loads(response2.content)
        
        # Los datos deben ser diferentes
        self.assertNotEqual(data1['gasto_total_mes'], data2['gasto_total_mes'])

    def test_multiple_requests_performance(self):
        """Test: Múltiples requests consecutivos (cache hit)"""
        times = []
        
        for i in range(5):
            start_time = time.time()
            response = self.client.get(reverse('dashboard_kpis_api'))
            end_time = time.time()
            
            times.append(end_time - start_time)
            self.assertEqual(response.status_code, 200)
        
        # El segundo request debería ser más rápido (cache hit)
        # En desarrollo con SQLite esto puede variar, pero debería ser consistente
        self.assertLess(max(times), 0.5)  # Todos los requests < 500ms


class ErrorHandlingAPITestCase(TestCase):
    """Tests para manejo de errores en APIs"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_api_without_authentication(self):
        """Test: API sin autenticación"""
        response = self.client.get(reverse('dashboard_kpis_api'))
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_api_with_invalid_parameters(self):
        """Test: API con parámetros inválidos"""
        self.client.login(username='testuser', password='testpass123')
        
        # Parámetros inválidos para autocompletar
        response = self.client.get(
            reverse('autocompletar_origen_movimiento'),
            {'invalid_param': 'test'}
        )
        
        # Debe manejar graciosamente
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

    def test_api_response_headers(self):
        """Test: Headers de respuesta correctos"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        
        self.assertEqual(response['Content-Type'], 'application/json')
        # En desarrollo, debe incluir headers de debug
        if hasattr(response, 'get'):
            debug_headers = ['X-Response-Time', 'X-DB-Queries']
            # Al menos uno de los headers de debug debería estar presente