from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core import mail
from django.http import JsonResponse
import json
from datetime import date, timedelta
from decimal import Decimal
from contabilidad_loslirios.models import MovimientoFinanciero, IngresoFinanciero, registro_trabajo

class DashboardViewsTestCase(TestCase):
    """Tests para las vistas del dashboard"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Crear datos de prueba
        self.create_test_data()

    def create_test_data(self):
        """Crear datos de prueba para los tests"""
        # Movimientos financieros
        MovimientoFinanciero.objects.create(
            fecha=date.today(),
            origen='Test Compra',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Cosecha',
            detalle='Herramientas',
            monto=Decimal('150.00'),
            moneda='USD',
            forma_pago='Efectivo'
        )
        
        # Ingresos
        IngresoFinanciero.objects.create(
            fecha=date.today(),
            origen='Venta Uva',
            destino='Bodega',
            comprador='Comprador Test',
            forma_pago='Efectivo',
            monto=Decimal('2000.00'),
            moneda='USD'
        )
        
        # Registro de trabajo
        registro_trabajo.objects.create(
            fecha=date.today(),
            nombre_trabajador='Juan Test',
            clasificacion='Cosecha',
            tarea='Corte',
            detalle='Test work',
            cantidad=Decimal('8.0'),
            unidad_medida='Horas',
            precio=Decimal('12.00'),
            ubicacion='Sector 1'
        )

    def test_main_view_requires_login(self):
        """Test: Vista principal requiere login"""
        self.client.logout()
        response = self.client.get(reverse('main'))
        
        self.assertRedirects(response, '/auth/login/?next=/')

    def test_main_view_with_login(self):
        """Test: Vista principal con usuario autenticado"""
        response = self.client.get(reverse('main'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Los Lirios')
        self.assertContains(response, 'Dashboard')

    def test_dashboard_kpis_api_response(self):
        """Test: API de KPIs retorna datos correctos"""
        response = self.client.get(reverse('dashboard_kpis_api'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        
        # Verificar estructura de respuesta
        self.assertIn('gasto_total_mes', data)
        self.assertIn('ingresos_mes', data)
        self.assertIn('saldo_disponible', data)
        self.assertIn('trabajadores_mes', data)
        
        # Verificar datos calculados
        self.assertEqual(float(data['gasto_total_mes']), 150.00)
        self.assertEqual(float(data['ingresos_mes']), 2000.00)
        self.assertEqual(float(data['saldo_disponible']), 1850.00)
        self.assertEqual(data['trabajadores_mes'], 1)

    def test_dashboard_kpis_api_without_data(self):
        """Test: API de KPIs sin datos devuelve ceros"""
        # Limpiar datos existentes
        MovimientoFinanciero.objects.all().delete()
        IngresoFinanciero.objects.all().delete()
        registro_trabajo.objects.all().delete()
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        data = json.loads(response.content)
        
        self.assertEqual(float(data['gasto_total_mes']), 0.0)
        self.assertEqual(float(data['ingresos_mes']), 0.0)
        self.assertEqual(data['trabajadores_mes'], 0)
        self.assertFalse(data['tiene_datos'])

    def test_dashboard_performance(self):
        """Test: Performance del dashboard con muchos datos"""
        import time
        
        # Crear muchos registros
        for i in range(100):
            MovimientoFinanciero.objects.create(
                fecha=date.today() - timedelta(days=i % 30),
                origen=f'Test {i}',
                finca='Los Lirios',
                tipo='Gasto',
                clasificacion='Cosecha',
                detalle=f'Test detail {i}',
                monto=Decimal(f'{i + 10}.00'),
                moneda='USD',
                forma_pago='Efectivo'
            )
        
        start_time = time.time()
        response = self.client.get(reverse('dashboard_kpis_api'))
        end_time = time.time()
        
        # El API debe responder en menos de 1 segundo
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(response.status_code, 200)


class FormViewsTestCase(TestCase):
    """Tests para vistas de formularios"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_cargar_movimiento_get(self):
        """Test: Vista GET de cargar movimiento"""
        response = self.client.get(reverse('cargar_movimientos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'Cargar Movimiento')

    def test_cargar_movimiento_post_valid(self):
        """Test: POST válido para cargar movimiento"""
        data = {
            'fecha': date.today(),
            'origen': 'Test Origen',
            'finca': 'Los Lirios',
            'tipo': 'Gasto',
            'clasificacion': 'Cosecha',
            'detalle': 'Test detalle',
            'monto': '150.50',
            'moneda': 'USD',
            'forma_pago': 'Efectivo'
        }
        
        response = self.client.post(reverse('cargar_movimientos'), data)
        
        # Debe redirigir después de crear exitosamente
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó el registro
        self.assertTrue(MovimientoFinanciero.objects.filter(origen='Test Origen').exists())

    def test_cargar_movimiento_post_invalid(self):
        """Test: POST inválido para cargar movimiento"""
        data = {
            'fecha': date.today(),
            'origen': '',  # Campo requerido vacío
            'monto': '-50.00',  # Monto negativo
            'moneda': 'USD'
        }
        
        response = self.client.post(reverse('cargar_movimientos'), data)
        
        # Debe retornar el formulario con errores
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # No debe crear el registro
        self.assertFalse(MovimientoFinanciero.objects.filter(origen='').exists())

    def test_cargar_ingreso_con_cheque(self):
        """Test: Cargar ingreso con datos de cheque"""
        data = {
            'fecha': date.today(),
            'origen': 'Venta Test',
            'destino': 'Cliente Test',
            'comprador': 'Comprador Test',
            'forma_pago': 'Cheque',
            'banco': 'Banco Test',
            'numero_cheque': 'CH123456',
            'fecha_pago': date.today() + timedelta(days=30),
            'monto': '5000.00',
            'moneda': 'USD'
        }
        
        response = self.client.post(reverse('cargar_ingresos'), data)
        
        self.assertEqual(response.status_code, 302)
        
        ingreso = IngresoFinanciero.objects.get(numero_cheque='CH123456')
        self.assertEqual(ingreso.banco, 'Banco Test')
        self.assertEqual(ingreso.forma_pago, 'Cheque')

    def test_autocompletar_origen_movimientos(self):
        """Test: Autocompletar origen en movimientos"""
        # Crear datos de prueba
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
        
        response = self.client.get(reverse('autocompletar_origen_movimiento'), {'term': 'Ferr'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('Ferretería Central', [item['value'] for item in data])


class ConsultaViewsTestCase(TestCase):
    """Tests para vistas de consulta y filtros"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Crear datos de prueba para filtros
        self.create_filter_test_data()

    def create_filter_test_data(self):
        """Crear datos específicos para probar filtros"""
        # Movimientos de diferentes meses
        MovimientoFinanciero.objects.create(
            fecha=date.today(),
            origen='Compra Actual',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Cosecha',
            detalle='Actual',
            monto=Decimal('100.00'),
            moneda='USD',
            forma_pago='Efectivo'
        )
        
        MovimientoFinanciero.objects.create(
            fecha=date.today() - timedelta(days=45),
            origen='Compra Antigua',
            finca='Los Lirios',
            tipo='Gasto',
            clasificacion='Insumos',
            detalle='Antigua',
            monto=Decimal('200.00'),
            moneda='USD',
            forma_pago='Tarjeta'
        )

    def test_consultar_movimientos_sin_filtros(self):
        """Test: Consulta de movimientos sin filtros muestra todos"""
        response = self.client.get(reverse('consultar_movimientos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compra Actual')
        self.assertContains(response, 'Compra Antigua')

    def test_consultar_movimientos_con_filtro_fecha(self):
        """Test: Filtro de movimientos por rango de fechas"""
        fecha_desde = date.today() - timedelta(days=7)
        fecha_hasta = date.today()
        
        response = self.client.get(reverse('consultar_movimientos'), {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compra Actual')
        self.assertNotContains(response, 'Compra Antigua')

    def test_consultar_movimientos_con_filtro_tipo(self):
        """Test: Filtro de movimientos por tipo"""
        response = self.client.get(reverse('consultar_movimientos'), {
            'tipo': 'Gasto'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compra Actual')
        self.assertContains(response, 'Compra Antigua')

    def test_consultar_movimientos_paginacion(self):
        """Test: Paginación en consulta de movimientos"""
        # Crear muchos registros para probar paginación
        for i in range(30):
            MovimientoFinanciero.objects.create(
                fecha=date.today(),
                origen=f'Compra {i}',
                finca='Los Lirios',
                tipo='Gasto',
                clasificacion='Test',
                detalle=f'Test {i}',
                monto=Decimal(f'{i + 10}.00'),
                moneda='USD',
                forma_pago='Efectivo'
            )
        
        response = self.client.get(reverse('consultar_movimientos'))
        
        self.assertEqual(response.status_code, 200)
        # Verificar que hay paginación
        self.assertContains(response, 'pagination')

    def test_exportar_movimientos_excel(self):
        """Test: Exportación de movimientos a Excel"""
        response = self.client.get(reverse('exportar_movimientos_excel'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'], 
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment', response['Content-Disposition'])


class APIViewsTestCase(TestCase):
    """Tests para endpoints de API"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_api_requires_authentication(self):
        """Test: APIs requieren autenticación"""
        self.client.logout()
        
        response = self.client.get(reverse('dashboard_kpis_api'))
        
        self.assertRedirects(response, '/auth/login/?next=/api/dashboard-kpis/')

    def test_api_performance_headers(self):
        """Test: APIs incluyen headers de performance"""
        response = self.client.get(reverse('dashboard_kpis_api'))
        
        self.assertEqual(response.status_code, 200)
        # En modo DEBUG, debe incluir headers de performance
        if hasattr(response, 'get'):
            self.assertIn('X-Response-Time', response.headers or {})

    def test_api_error_handling(self):
        """Test: Manejo de errores en APIs"""
        # Simular error en base de datos (esto requeriría más setup)
        response = self.client.get(reverse('dashboard_kpis_api'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Debe tener estructura de respuesta consistente
        self.assertIn('success', data)
        self.assertIn('timestamp', data)