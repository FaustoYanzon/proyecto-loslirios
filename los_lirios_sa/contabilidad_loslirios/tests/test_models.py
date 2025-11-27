from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.db.models import Sum
from contabilidad_loslirios.models import (
    MovimientoFinanciero, IngresoFinanciero, registro_trabajo,
    RegistroRiego, RegistroCosecha, Parcela
)

class MovimientoFinancieroTestCase(TestCase):
    """Tests para el modelo MovimientoFinanciero"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_pass'
        )
        
        self.movimiento_data = {
            'fecha': date.today(),
            'origen': 'Test Origen',
            'finca': 'Los Lirios',
            'tipo': 'Gasto',
            'clasificacion': 'Cosecha',
            'detalle': 'Compra de herramientas',
            'monto': Decimal('150.00'),
            'moneda': 'USD',
            'forma_pago': 'Efectivo'
        }

    def test_crear_movimiento_financiero_valido(self):
        """Test: Crear movimiento financiero con datos válidos"""
        movimiento = MovimientoFinanciero.objects.create(**self.movimiento_data)
        
        self.assertEqual(movimiento.origen, 'Test Origen')
        self.assertEqual(movimiento.monto, Decimal('150.00'))
        self.assertEqual(movimiento.tipo, 'Gasto')
        self.assertIsNotNone(movimiento.id_movimiento)

    def test_str_representation(self):
        """Test: Representación string del modelo"""
        movimiento = MovimientoFinanciero.objects.create(**self.movimiento_data)
        expected_str = f"Gasto - Test Origen - $150.00 ({date.today()})"
        
        self.assertEqual(str(movimiento), expected_str)

    def test_monto_no_puede_ser_negativo(self):
        """Test: Validación de monto no negativo"""
        self.movimiento_data['monto'] = Decimal('-50.00')
        
        with self.assertRaises(ValidationError):
            movimiento = MovimientoFinanciero(**self.movimiento_data)
            movimiento.full_clean()

    def test_fecha_no_puede_ser_futura(self):
        """Test: Validación de fecha no futura"""
        self.movimiento_data['fecha'] = date.today() + timedelta(days=1)
        
        with self.assertRaises(ValidationError):
            movimiento = MovimientoFinanciero(**self.movimiento_data)
            movimiento.full_clean()

    def test_filtros_por_rango_fecha(self):
        """Test: Filtros por rango de fechas"""
        # Crear movimientos con diferentes fechas
        MovimientoFinanciero.objects.create(
            **{**self.movimiento_data, 'fecha': date.today() - timedelta(days=5)}
        )
        MovimientoFinanciero.objects.create(
            **{**self.movimiento_data, 'fecha': date.today()}
        )
        MovimientoFinanciero.objects.create(
            **{**self.movimiento_data, 'fecha': date.today() - timedelta(days=10)}
        )

        # Filtrar últimos 7 días
        fecha_desde = date.today() - timedelta(days=7)
        movimientos_recientes = MovimientoFinanciero.objects.filter(
            fecha__gte=fecha_desde
        )

        self.assertEqual(movimientos_recientes.count(), 2)


class IngresoFinancieroTestCase(TestCase):
    """Tests para el modelo IngresoFinanciero"""
    
    def setUp(self):
        """Configuración inicial"""
        self.ingreso_data = {
            'fecha': date.today(),
            'origen': 'Venta Uva',
            'destino': 'Exportación',
            'comprador': 'Buyer Corp',
            'forma_pago': 'Cheque',
            'forma': 'Cheque diferido',
            'banco': 'Banco Test',
            'numero_cheque': 'CH001234',
            'fecha_pago': date.today() + timedelta(days=30),
            'monto': Decimal('5000.00'),
            'moneda': 'USD'
        }

    def test_crear_ingreso_con_cheque(self):
        """Test: Crear ingreso con forma de pago cheque"""
        ingreso = IngresoFinanciero.objects.create(**self.ingreso_data)
        
        self.assertEqual(ingreso.forma_pago, 'Cheque')
        self.assertEqual(ingreso.numero_cheque, 'CH001234')
        self.assertEqual(ingreso.banco, 'Banco Test')
        self.assertIsNotNone(ingreso.fecha_pago)

    def test_ingreso_efectivo_sin_cheque_data(self):
        """Test: Ingreso en efectivo no requiere datos de cheque"""
        self.ingreso_data.update({
            'forma_pago': 'Efectivo',
            'numero_cheque': '',
            'banco': '',
            'fecha_pago': None
        })
        
        ingreso = IngresoFinanciero.objects.create(**self.ingreso_data)
        
        self.assertEqual(ingreso.forma_pago, 'Efectivo')
        self.assertEqual(ingreso.numero_cheque, '')
        self.assertIsNone(ingreso.fecha_pago)

    def test_cheques_proximos_vencimiento(self):
        """Test: Query para cheques próximos a vencer"""
        # Crear cheques con diferentes fechas de vencimiento
        IngresoFinanciero.objects.create(
            **{**self.ingreso_data, 
               'fecha_pago': date.today() + timedelta(days=5)}
        )
        IngresoFinanciero.objects.create(
            **{**self.ingreso_data, 
               'numero_cheque': 'CH002',
               'fecha_pago': date.today() + timedelta(days=45)}
        )

        # Buscar cheques que vencen en 30 días
        fecha_limite = date.today() + timedelta(days=30)
        cheques_proximos = IngresoFinanciero.objects.filter(
            forma_pago__in=['Cheque', 'Echeque'],
            fecha_pago__lte=fecha_limite,
            fecha_pago__gte=date.today()
        )

        self.assertEqual(cheques_proximos.count(), 1)

    def test_validacion_monto_positivo(self):
        """Test: Monto debe ser positivo"""
        self.ingreso_data['monto'] = Decimal('0')
        
        with self.assertRaises(ValidationError):
            ingreso = IngresoFinanciero(**self.ingreso_data)
            ingreso.full_clean()


class RegistroTrabajoTestCase(TestCase):
    """Tests para el modelo registro_trabajo"""
    
    def setUp(self):
        """Configuración inicial"""
        self.trabajo_data = {
            'fecha': date.today(),
            'nombre_trabajador': 'Juan Pérez',
            'clasificacion': 'Cosecha',
            'tarea': 'Corte de uva',
            'detalle': 'Parral 1-A',
            'cantidad': Decimal('8.5'),
            'unidad_medida': 'Horas',
            'precio': Decimal('12.00'),
            'ubicacion': 'Sector Norte'
        }

    def test_calculo_automatico_monto_total(self):
        """Test: Cálculo automático de monto_total"""
        trabajo = registro_trabajo.objects.create(**self.trabajo_data)
        
        expected_monto = Decimal('8.5') * Decimal('12.00')  # 102.00
        self.assertEqual(trabajo.monto_total, expected_monto)

    def test_str_representation(self):
        """Test: Representación string"""
        trabajo = registro_trabajo.objects.create(**self.trabajo_data)
        expected_str = f"Juan Pérez - Corte de uva ({date.today()})"
        
        self.assertEqual(str(trabajo), expected_str)

    def test_trabajadores_activos_periodo(self):
        """Test: Consulta de trabajadores activos en un período"""
        # Crear registros de diferentes trabajadores
        registro_trabajo.objects.create(**self.trabajo_data)
        registro_trabajo.objects.create(**{
            **self.trabajo_data,
            'nombre_trabajador': 'María González'
        })
        registro_trabajo.objects.create(**{
            **self.trabajo_data,
            'nombre_trabajador': 'Juan Pérez',  # Mismo trabajador
            'fecha': date.today() - timedelta(days=1)
        })

        # Contar trabajadores únicos
        trabajadores_unicos = registro_trabajo.objects.filter(
            fecha__gte=date.today() - timedelta(days=7)
        ).values('nombre_trabajador').distinct().count()

        self.assertEqual(trabajadores_unicos, 2)

    def test_validacion_cantidad_positiva(self):
        """Test: Cantidad debe ser positiva"""
        self.trabajo_data['cantidad'] = Decimal('0')
        
        with self.assertRaises(ValidationError):
            trabajo = registro_trabajo(**self.trabajo_data)
            trabajo.full_clean()

    def test_validacion_precio_positivo(self):
        """Test: Precio debe ser positivo"""
        self.trabajo_data['precio'] = Decimal('-5.00')
        
        with self.assertRaises(ValidationError):
            trabajo = registro_trabajo(**self.trabajo_data)
            trabajo.full_clean()


class RegistroCosechaTestCase(TestCase):
    """Tests para el modelo RegistroCosecha"""
    
    def setUp(self):
        """Configuración inicial"""
        self.cosecha_data = {
            'fecha': date.today(),
            'finca': 'Los Lirios',
            'variedad': 'Cabernet Sauvignon',
            'kg_totales': Decimal('1500.50'),
            'destino': 'Bodega XYZ',
            'comprador': 'Vinos del Valle',
            'origen': 'Parral 1'
        }

    def test_crear_registro_cosecha(self):
        """Test: Crear registro de cosecha válido"""
        cosecha = RegistroCosecha.objects.create(**self.cosecha_data)
        
        self.assertEqual(cosecha.finca, 'Los Lirios')
        self.assertEqual(cosecha.kg_totales, Decimal('1500.50'))
        self.assertEqual(cosecha.variedad, 'Cabernet Sauvignon')

    def test_validacion_kg_positivos(self):
        """Test: Kg totales deben ser positivos"""
        self.cosecha_data['kg_totales'] = Decimal('0')
        
        with self.assertRaises(ValidationError):
            cosecha = RegistroCosecha(**self.cosecha_data)
            cosecha.full_clean()

    def test_cosecha_por_variedad_periodo(self):
        """Test: Consulta de cosecha por variedad en período"""
        # Crear registros de diferentes variedades
        RegistroCosecha.objects.create(**self.cosecha_data)
        RegistroCosecha.objects.create(**{
            **self.cosecha_data,
            'variedad': 'Merlot',
            'kg_totales': Decimal('800.25')
        })

        # Total por variedad
        from django.db.models import Sum
        total_cabernet = RegistroCosecha.objects.filter(
            variedad='Cabernet Sauvignon',
            fecha__gte=date.today() - timedelta(days=7)
        ).aggregate(total=Sum('kg_totales'))['total']

        self.assertEqual(total_cabernet, Decimal('1500.50'))


class RegistroRiegoTestCase(TestCase):
    """Tests para el modelo RegistroRiego"""
    
    def setUp(self):
        """Configuración inicial"""
        self.riego_data = {
            'cabezal': 'Cabezal Norte',
            'parral': 'Parral 1-A',
            'valvula_abierta': '1, 3, 5',
            'inicio': datetime.now(),
            'fin': datetime.now() + timedelta(hours=2),
            'responsable': 'Carlos Riego'
        }

    def test_crear_registro_riego(self):
        """Test: Crear registro de riego válido"""
        riego = RegistroRiego.objects.create(**self.riego_data)
        
        self.assertEqual(riego.cabezal, 'Cabezal Norte')
        self.assertEqual(riego.responsable, 'Carlos Riego')
        self.assertIsNotNone(riego.inicio)

    def test_duracion_riego(self):
        """Test: Calcular duración de riego"""
        riego = RegistroRiego.objects.create(**self.riego_data)
        
        duracion = riego.fin - riego.inicio
        self.assertEqual(duracion.seconds, 7200)  # 2 horas = 7200 segundos

    def test_riego_activo_sin_fin(self):
        """Test: Registro de riego activo (sin hora fin)"""
        self.riego_data['fin'] = None
        riego = RegistroRiego.objects.create(**self.riego_data)
        
        self.assertIsNone(riego.fin)
        self.assertIsNotNone(riego.inicio)