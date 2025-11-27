from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta
from contabilidad_loslirios.forms import (
    FormMovimientoFinanciero, FormIngresoFinanciero, FormRegistroTrabajo,
    FormConsultaMovimiento, FormConsultaIngresos, FormConsultaJornal,
    FormRegistroRiego, FormRegistroCosecha
)

class FormMovimientoFinancieroTestCase(TestCase):
    """Tests para el formulario de movimientos financieros"""
    
    def test_form_valid_data(self):
        """Test: Formulario con datos válidos"""
        form_data = {
            'fecha': date.today(),
            'origen': 'Ferretería Central',
            'finca': 'Los Lirios',
            'tipo': 'Gasto',
            'clasificacion': 'Cosecha',
            'detalle': 'Compra de herramientas',
            'monto': '150.50',
            'moneda': 'USD',
            'forma_pago': 'Efectivo'
        }
        
        form = FormMovimientoFinanciero(data=form_data)
        
        self.assertTrue(form.is_valid(), f"Errores del formulario: {form.errors}")

    def test_form_missing_required_fields(self):
        """Test: Formulario con campos requeridos faltantes"""
        form_data = {
            'fecha': date.today(),
            'monto': '150.50'
            # Faltan campos requeridos
        }
        
        form = FormMovimientoFinanciero(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('origen', form.errors)
        self.assertIn('tipo', form.errors)

    def test_form_negative_amount(self):
        """Test: Validación de monto negativo"""
        form_data = {
            'fecha': date.today(),
            'origen': 'Test',
            'finca': 'Los Lirios',
            'tipo': 'Gasto',
            'clasificacion': 'Cosecha',
            'detalle': 'Test',
            'monto': '-50.00',  # Monto negativo
            'moneda': 'USD',
            'forma_pago': 'Efectivo'
        }
        
        form = FormMovimientoFinanciero(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_form_future_date(self):
        """Test: Validación de fecha futura"""
        form_data = {
            'fecha': date.today() + timedelta(days=1),  # Fecha futura
            'origen': 'Test',
            'finca': 'Los Lirios',
            'tipo': 'Gasto',
            'clasificacion': 'Cosecha',
            'detalle': 'Test',
            'monto': '50.00',
            'moneda': 'USD',
            'forma_pago': 'Efectivo'
        }
        
        form = FormMovimientoFinanciero(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('fecha', form.errors)

    def test_form_choices_validation(self):
        """Test: Validación de opciones válidas"""
        form_data = {
            'fecha': date.today(),
            'origen': 'Test',
            'finca': 'Los Lirios',
            'tipo': 'TipoInvalido',  # Tipo no válido
            'clasificacion': 'Cosecha',
            'detalle': 'Test',
            'monto': '50.00',
            'moneda': 'USD',
            'forma_pago': 'Efectivo'
        }
        
        form = FormMovimientoFinanciero(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('tipo', form.errors)


class FormIngresoFinancieroTestCase(TestCase):
    """Tests para el formulario de ingresos financieros"""
    
    def test_ingreso_efectivo_valid(self):
        """Test: Ingreso en efectivo válido"""
        form_data = {
            'fecha': date.today(),
            'origen': 'Venta Uva',
            'destino': 'Cliente Local',
            'comprador': 'Juan Cliente',
            'forma_pago': 'Efectivo',
            'monto': '2000.00',
            'moneda': 'USD'
        }
        
        form = FormIngresoFinanciero(data=form_data)
        
        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_ingreso_cheque_valid(self):
        """Test: Ingreso con cheque válido"""
        form_data = {
            'fecha': date.today(),
            'origen': 'Venta Uva',
            'destino': 'Cliente',
            'comprador': 'Cliente Corp',
            'forma_pago': 'Cheque',
            'banco': 'Banco Test',
            'numero_cheque': 'CH123456',
            'fecha_pago': date.today() + timedelta(days=30),
            'monto': '5000.00',
            'moneda': 'USD'
        }
        
        form = FormIngresoFinanciero(data=form_data)
        
        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_cheque_missing_bank_data(self):
        """Test: Cheque sin datos bancarios"""
        form_data = {
            'fecha': date.today(),
            'origen': 'Venta',
            'destino': 'Cliente',
            'comprador': 'Cliente Corp',
            'forma_pago': 'Cheque',
            # Faltan: banco, numero_cheque, fecha_pago
            'monto': '5000.00',
            'moneda': 'USD'
        }
        
        form = FormIngresoFinanciero(data=form_data)
        
        self.assertFalse(form.is_valid())
        # Debe requerir datos bancarios para cheques
        self.assertTrue(
            'banco' in form.errors or 
            'numero_cheque' in form.errors or 
            'fecha_pago' in form.errors
        )

    def test_zero_amount_validation(self):
        """Test: Validación de monto cero"""
        form_data = {
            'fecha': date.today(),
            'origen': 'Test',
            'destino': 'Test',
            'comprador': 'Test',
            'forma_pago': 'Efectivo',
            'monto': '0.00',  # Monto cero
            'moneda': 'USD'
        }
        
        form = FormIngresoFinanciero(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)


class FormRegistroTrabajoTestCase(TestCase):
    """Tests para el formulario de registro de trabajo"""
    
    def test_trabajo_valid_data(self):
        """Test: Registro de trabajo con datos válidos"""
        form_data = {
            'fecha': date.today(),
            'nombre_trabajador': 'Juan Trabajador',
            'clasificacion': 'Cosecha',
            'tarea': 'Corte de uva',
            'detalle': 'Parral 1-A',
            'cantidad': '8.5',
            'unidad_medida': 'Horas',
            'precio': '12.00',
            'ubicacion': 'Sector Norte'
        }
        
        form = FormRegistroTrabajo(data=form_data)
        
        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_trabajo_cantidad_negativa(self):
        """Test: Cantidad negativa no válida"""
        form_data = {
            'fecha': date.today(),
            'nombre_trabajador': 'Juan',
            'clasificacion': 'Cosecha',
            'tarea': 'Corte',
            'cantidad': '-2.0',  # Cantidad negativa
            'unidad_medida': 'Horas',
            'precio': '12.00',
            'ubicacion': 'Test'
        }
        
        form = FormRegistroTrabajo(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)

    def test_trabajo_precio_negativo(self):
        """Test: Precio negativo no válido"""
        form_data = {
            'fecha': date.today(),
            'nombre_trabajador': 'Juan',
            'clasificacion': 'Cosecha',
            'tarea': 'Corte',
            'cantidad': '8.0',
            'unidad_medida': 'Horas',
            'precio': '-5.00',  # Precio negativo
            'ubicacion': 'Test'
        }
        
        form = FormRegistroTrabajo(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)


class FormConsultasTestCase(TestCase):
    """Tests para formularios de consulta y filtros"""
    
    def test_consulta_movimiento_empty_valid(self):
        """Test: Formulario de consulta vacío es válido"""
        form = FormConsultaMovimiento(data={})
        
        self.assertTrue(form.is_valid())

    def test_consulta_movimiento_rango_fechas(self):
        """Test: Consulta con rango de fechas válido"""
        form_data = {
            'fecha_desde': date.today() - timedelta(days=30),
            'fecha_hasta': date.today()
        }
        
        form = FormConsultaMovimiento(data=form_data)
        
        self.assertTrue(form.is_valid())

    def test_consulta_movimiento_rango_fechas_invalido(self):
        """Test: Rango de fechas inválido (desde > hasta)"""
        form_data = {
            'fecha_desde': date.today(),
            'fecha_hasta': date.today() - timedelta(days=1)  # Fecha hasta menor
        }
        
        form = FormConsultaMovimiento(data=form_data)
        
        self.assertFalse(form.is_valid())

    def test_consulta_ingresos_filtros(self):
        """Test: Formulario de consulta de ingresos con filtros"""
        form_data = {
            'fecha_desde': date.today() - timedelta(days=30),
            'origen': 'Venta',
            'forma_pago': 'Cheque'
        }
        
        form = FormConsultaIngresos(data=form_data)
        
        self.assertTrue(form.is_valid())

    def test_consulta_jornal_trabajador(self):
        """Test: Consulta de jornal por trabajador"""
        form_data = {
            'nombre_trabajador': 'Juan',
            'clasificacion': 'Cosecha',
            'fecha_desde': date.today() - timedelta(days=7)
        }
        
        form = FormConsultaJornal(data=form_data)
        
        self.assertTrue(form.is_valid())


class FormCosechaRiegoTestCase(TestCase):
    """Tests para formularios de cosecha y riego"""
    
    def test_registro_cosecha_valid(self):
        """Test: Registro de cosecha válido"""
        form_data = {
            'fecha': date.today(),
            'finca': 'Los Lirios',
            'variedad': 'Cabernet Sauvignon',
            'kg_totales': '1500.50',
            'destino': 'Bodega XYZ',
            'comprador': 'Vinos del Valle',
            'origen': 'Parral 1'
        }
        
        form = FormRegistroCosecha(data=form_data)
        
        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_registro_cosecha_kg_negativos(self):
        """Test: Kg negativos no válidos"""
        form_data = {
            'fecha': date.today(),
            'finca': 'Los Lirios',
            'variedad': 'Cabernet',
            'kg_totales': '-100.0',  # Kg negativos
            'destino': 'Bodega',
            'comprador': 'Cliente',
            'origen': 'Parral'
        }
        
        form = FormRegistroCosecha(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('kg_totales', form.errors)

    def test_registro_riego_valid(self):
        """Test: Registro de riego válido"""
        from datetime import datetime
        
        form_data = {
            'cabezal': 'Cabezal Norte',
            'parral': 'Parral 1-A',
            'valvula_abierta': '1, 3, 5',
            'inicio': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'responsable': 'Carlos Riego'
        }
        
        form = FormRegistroRiego(data=form_data)
        
        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_registro_riego_fin_antes_inicio(self):
        """Test: Hora fin antes de inicio no válida"""
        from datetime import datetime, timedelta
        
        ahora = datetime.now()
        
        form_data = {
            'cabezal': 'Cabezal Norte',
            'parral': 'Parral 1-A',
            'valvula_abierta': '1, 3',
            'inicio': ahora.strftime('%Y-%m-%d %H:%M'),
            'fin': (ahora - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),  # Fin antes de inicio
            'responsable': 'Carlos'
        }
        
        form = FormRegistroRiego(data=form_data)
        
        self.assertFalse(form.is_valid())