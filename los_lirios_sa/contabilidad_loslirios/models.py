from datetime import date
from django.db import models

# Create your models here.

#Model for main page 
class Parcela(models.Model):
    """
    Representa una parcela individual (parral, potrero, etc.) en una finca.
    """
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre único de la parcela, ej: 'Parral 16'")
    variedad = models.CharField(max_length=100, null=True, blank=True)
    superficie_ha = models.FloatField(null=True, blank=True, verbose_name="Superficie (ha)")
    cabezal_riego = models.CharField(max_length=50, null=True, blank=True, verbose_name="Cabezal de Riego")
    coordenadas = models.JSONField(null=True, help_text="Lista de coordenadas [[lat, lon], ...] que forman el polígono.")

    class Meta:
        verbose_name = "Parcela"
        verbose_name_plural = "Parcelas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

#Administration

#Model for daily work
# Choices for the classification field
CLASIFICACION_CHOICES = [
    ('General', 'General'),
    ('Verano', 'Verano'),
    ('Otoño', 'Otoño'),
    ('Invierno', 'Invierno'),
    ('Primavera', 'Primavera'),
]

class registro_trabajo(models.Model):
    id_registro = models.AutoField(primary_key=True)
    fecha = models.DateField()
    nombre_trabajador = models.CharField(max_length=50)
    clasificacion = models.CharField(
        max_length=20,
        choices=CLASIFICACION_CHOICES,
        default='General')
    detalle = models.CharField(max_length=255,default='N/A')
    tarea = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    ubicacion = models.CharField(max_length=50)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2)

    def save(self, *args, **kwargs):
        self.monto_total = self.cantidad * self.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return(f"{self.fecha} - {self.nombre_trabajador} - {self.tarea}")
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.cantidad is not None and self.cantidad <= 0:
            raise ValidationError({'cantidad': 'La cantidad debe ser mayor a cero'})
        if self.precio is not None and self.precio <= 0:
            raise ValidationError({'precio': 'El precio debe ser mayor a cero'})

    class Meta:
        verbose_name = "Registro de Trabajo"
        verbose_name_plural = "Registros de Trabajo"
        indexes = [
            models.Index(fields=['fecha']),  # Consultas por fecha (muy frecuente)
            models.Index(fields=['nombre_trabajador']),  # Búsquedas por trabajador
            models.Index(fields=['clasificacion']),  # Filtros por temporada
            models.Index(fields=['ubicacion']),  # Filtros por ubicación
            models.Index(fields=['fecha', 'clasificacion']),  # Consultas combinadas del dashboard
            models.Index(fields=['fecha', 'nombre_trabajador']),  # Análisis por trabajador y fecha
            models.Index(fields=['tarea']),  # Filtros por tarea
        ]
        permissions = [
            ("can_view_jornales", "Can view all jornal entries"),
            ("can_add_jornales", "Can add new jornal entries"),
            ("can_export_jornales", "Can export jornal data"),
        ]

#Modelo para Movimientos Financieros 
# Opciones para Movimimientos Financierons Egresos
ORIGEN_CHOICES = [('Oficial', 'Oficial'), ('No Oficial', 'No Oficial')]

FINCA_CHOICES = [('Los Mimbres', 'Los Mimbres'), ('Media Agua', 'Media Agua'), ('Caucete', 'Caucete')]

TIPO_MOVIMIENTO_CHOICES = [('Sueldos Personal', 'Sueldos Personal'),
    ('Produccion', 'Producción'),
    ('Inversion', 'Inversión'),
    ('Repuestos y Reparaciones', 'Repuestos y Reparaciones'),
    ('Insumos Varios', 'Insumos Varios'),
    ('Impuestos o Servicios', 'Impuestos o Servicios'),
    ('Energia', 'Energía'),]

MONEDA_CHOICES = [('ARS', 'Pesos'), ('USD', 'USD')]

FORMA_PAGO_CHOICES = [('Efectivo', 'Efectivo'),
    ('Transferencia', 'Transferencia'),
    ('Credito', 'Crédito'),
    ('Cheque', 'Cheque'),]

#Modelo Movimiento Financiero Egresos
class MovimientoFinanciero(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    fecha = models.DateField()
    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES)
    finca = models.CharField(max_length=20, choices=FINCA_CHOICES)
    tipo = models.CharField(max_length=30, choices=TIPO_MOVIMIENTO_CHOICES)
    clasificacion = models.CharField(max_length=50) 
    detalle = models.TextField(blank=True, null=True) 
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES)
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES)

    def __str__(self):
        return f"{self.fecha} | {self.tipo} ({self.clasificacion}) - {self.moneda} {self.monto}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.monto is not None and self.monto < 0:
            raise ValidationError({'monto': 'El monto no puede ser negativo'})
        if self.fecha and self.fecha > date.today():
            raise ValidationError({'fecha': 'La fecha no puede ser futura'})
    
    class Meta:
        verbose_name = "Movimiento Financiero"
        verbose_name_plural = "Movimientos Financieros"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),  
            models.Index(fields=['tipo']),  
            models.Index(fields=['clasificacion']),  
            models.Index(fields=['origen']),  
            models.Index(fields=['finca']),  
            models.Index(fields=['forma_pago']),  
            models.Index(fields=['fecha', 'tipo']),  
            models.Index(fields=['fecha', 'origen']),  
            models.Index(fields=['moneda', 'fecha']),  
            models.Index(fields=['monto']),  
        ]
        permissions = [
            ("can_view_movimientos", "Can view all financial movements"),
            ("can_add_movimientos", "Can add new financial movements"),
            ("can_export_movimientos", "Can export financial movements data"),
        ]
#Modelo Movimiento Financiero Ingresos
DESTINO_INGRESOS_CHOICES = [
    ('Alfalfa', 'Alfalfa'),
    ('Alquiler', 'Alquiler'),
    ('Bodega', 'Bodega'),
    ('Cebolla', 'Cebolla'),
    ('Pasa', 'Pasa'),
    ('Sandia', 'Sandía'),
    ('Uva de mesa', 'Uva de mesa'),
]

FORMA_PAGO_INGRESOS_CHOICES = [
    ('Cheque', 'Cheque'),
    ('Efectivo', 'Efectivo'),
    ('Transferencia', 'Transferencia'),
    ('Echeque', 'Echeque'),
]

FORMA_CHOICES = [
    ('Caja', 'Caja'),
    ('Bsj', 'Bsj'),
    ('MP camilo', 'MP camilo'),
    ('GM', 'GM'),
    ('Naranja Nico', 'Naranja Nico'),
    ('Galicia Nico', 'Galicia Nico'),
]

class DestinoIngreso(models.Model):
    """Modelo para gestionar destinos personalizados de ingresos"""
    nombre = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Destino de Ingreso"
        verbose_name_plural = "Destinos de Ingresos"
        ordering = ['nombre']

class CompradorIngreso(models.Model):
    """Modelo para gestionar compradores personalizados de ingresos"""
    nombre = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Comprador de Ingreso"
        verbose_name_plural = "Compradores de Ingresos"
        ordering = ['nombre']

class IngresoFinanciero(models.Model):
    id_ingreso = models.AutoField(primary_key=True)
    fecha = models.DateField()
    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES)
    destino = models.CharField(max_length=100, verbose_name="Destino")
    comprador = models.CharField(max_length=100, verbose_name="Comprador")
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_INGRESOS_CHOICES)
    forma = models.CharField(max_length=50, choices=FORMA_CHOICES)
    
    # Campos que se desbloquean solo si forma_pago es Cheque o Echeque
    banco = models.CharField(max_length=100, blank=True, null=True)
    numero_cheque = models.CharField(max_length=50, blank=True, null=True, verbose_name="N° de Cheque")
    fecha_pago = models.DateField(blank=True, null=True, verbose_name="Fecha de Pago")
    
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES)

    def clean(self):
        """Validación personalizada para campos condicionales"""
        from django.core.exceptions import ValidationError
        
        # Si forma_pago es Cheque o Echeque, banco, numero_cheque y fecha_pago son obligatorios
        if self.forma_pago in ['Cheque', 'Echeque']:
            if not self.banco:
                raise ValidationError({'banco': 'Este campo es obligatorio cuando la forma de pago es Cheque o Echeque.'})
            if not self.numero_cheque:
                raise ValidationError({'numero_cheque': 'Este campo es obligatorio cuando la forma de pago es Cheque o Echeque.'})
            if not self.fecha_pago:
                raise ValidationError({'fecha_pago': 'Este campo es obligatorio cuando la forma de pago es Cheque o Echeque.'})
        else:
            # Si no es Cheque o Echeque, limpiar estos campos
            self.banco = None
            self.numero_cheque = None
            self.fecha_pago = None

    def __str__(self):
        return f"{self.fecha} | {self.destino} - {self.comprador} - {self.moneda} {self.monto}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.monto is not None and self.monto <= 0:
            raise ValidationError({'monto': 'El monto debe ser mayor a cero'})
        if self.fecha and self.fecha > date.today():
            raise ValidationError({'fecha': 'La fecha no puede ser futura'})

    class Meta:
        verbose_name = "Ingreso Financiero"
        verbose_name_plural = "Ingresos Financieros"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),  # Consultas por fecha (muy frecuente)
            models.Index(fields=['forma_pago']),  # Para filtros de cheques
            models.Index(fields=['fecha_pago']),  # Para cheques próximos a vencer (CRÍTICO)
            models.Index(fields=['comprador']),  # Búsquedas por comprador
            models.Index(fields=['destino']),  # Filtros por destino
            models.Index(fields=['origen']),  # Filtros por origen
            models.Index(fields=['forma_pago', 'fecha_pago']),  # Cheques pendientes (Dashboard)
            models.Index(fields=['fecha', 'forma_pago']),  # KPIs del dashboard
            models.Index(fields=['monto']),  # Para agregaciones
        ]
        permissions = [
            ("can_view_ingresos", "Can view all financial incomes"),
            ("can_add_ingresos", "Can add new financial incomes"),
            ("can_export_ingresos", "Can export financial incomes data"),
        ]


# Production

#Model for  Irrigation and Fertilization
class RegistroRiego(models.Model):
    id_riego = models.AutoField(primary_key=True)
    cabezal = models.CharField(max_length=50, verbose_name="Cabezal")
    parral = models.CharField(max_length=100, verbose_name="Parral/Potrero")
    valvula_abierta = models.CharField(max_length=50, help_text="Valvulas seleccionadas, ej: '1,3'")
    inicio = models.DateTimeField(verbose_name="Inicio de Operación")
    fin = models.DateTimeField(verbose_name="Fin de Operación")
    fertilizante_nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre del Fertilizante")
    fertilizante_litros = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Litros de Fertilizante")
    responsable = models.CharField(max_length=100)

    @property
    def total_horas(self):
        """Calcula la duración total del riego en horas."""
        if self.inicio and self.fin and self.fin > self.inicio:
            # La diferencia es un objeto timedelta
            diferencia = self.fin - self.inicio
            # Convertimos la diferencia a horas (total_seconds / 3600)
            return round(diferencia.total_seconds() / 3600, 2)
        return 0

    def __str__(self):
        return f"Riego en {self.parral} ({self.cabezal}) - {self.inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fin and self.inicio and self.fin <= self.inicio:
            raise ValidationError({'fin': 'La fecha y hora de fin debe ser posterior a la de inicio'})
        if self.fertilizante_litros is not None and self.fertilizante_litros < 0:
            raise ValidationError({'fertilizante_litros': 'Los litros de fertilizante no pueden ser negativos'})

    class Meta:
        verbose_name = "Registro de Riego"
        verbose_name_plural = "Registros de Riego"
        ordering = ['-inicio']
        indexes = [
            models.Index(fields=['inicio']),  # Consultas por fecha de inicio
            models.Index(fields=['cabezal']),  # Filtros por cabezal
            models.Index(fields=['parral']),  # Filtros por parral
            models.Index(fields=['responsable']),  # Filtros por responsable
            models.Index(fields=['inicio', 'cabezal']),  # Consultas combinadas
        ]
        permissions = [
            ("can_view_riego", "Can view irrigation data"),
            ("can_add_riego", "Can add new irrigation entries"),
        ]

# Modelo for Cosecha
ORIGEN_CHOICES = [
    ('Terceros', 'Terceros'),
    ('Los Lirios', 'Los Lirios'),
]

FINCA_CHOICES = [
    ('Mediagua', 'Mediagua'),
    ('Caucete', 'Caucete'),
    ('9 de Julio', '9 de Julio'),
]

DESTINO_CHOICES = [
    ('Bodega', 'Bodega'),
    ('Descarte', 'Descarte'),
    ('Exportacion', 'Exportación'),
    ('Fardo', 'Fardo'),
    ('Mercado Interno', 'Mercado Interno'),
    ('Pasa', 'Pasa'),
    ('Rama Pasa', 'Rama Pasa'),
    ('Semilla', 'Semilla'),
]

COMPRADOR_CHOICES = [
    ('Pasero', 'Pasero'),
    ('Natural Food', 'Natural Food'),
    ('Vizcaino', 'Vizcaino'),
]

CULTIVO_CHOICES = [
    ('Alfalfa', 'Alfalfa'),
    ('Chacra', 'Chacra'),
    ('Ind Pasa', 'Ind Pasa'),
    ('VID', 'VID'),
]

VARIEDAD_CHOICES = [
    ('Alfalfa', 'Alfalfa'),
    ('Alfalfa 969', 'Alfalfa 969'),
    ('Alfalfa GL', 'Alfalfa GL'),
    ('Alfalfa Mecha', 'Alfalfa Mecha'),
    ('Aspirant', 'Aspirant'),
    ('Bonarda', 'Bonarda'),
    ('Fiesta', 'Fiesta'),
    ('Flame', 'Flame'),
    ('Red Globe', 'Red Globe'),
    ('Sandia', 'Sandía'),
    ('Sultanina', 'Sultanina'),
    ('Superior', 'Superior'),
    ('Syrah', 'Syrah'),
    ('Zapallo', 'Zapallo'),
]

MEDIDA_CHOICES = [
    ('Caja', 'Caja'),
    ('Bin', 'Bin'),
    ('Chasis', 'Chasis'),
]

class RegistroCosecha(models.Model):
    fecha = models.DateField()
    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES)
    finca = models.CharField(max_length=50)
    destino = models.CharField(max_length=50, choices=DESTINO_CHOICES)
    comprador = models.CharField(max_length=100)
    cultivo = models.CharField(max_length=50)
    parral_potrero = models.CharField(max_length=100, verbose_name="Parral/Potrero")
    variedad = models.CharField(max_length=50)
    remito = models.CharField(max_length=50, verbose_name="Número de Remito")
    ciu = models.IntegerField(blank=True, null=True, verbose_name="CIU (Solo para uva de bodega)")
    medida = models.CharField(max_length=20, choices=MEDIDA_CHOICES)
    peso_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Peso Unitario (Kg)")
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad de cajas/bins")
    bruto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Peso Bruto (Kg)")
    tara = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Tara (Kg)")
    kg_totales = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kg Totales")
    
    def save(self, *args, **kwargs):
        # Calcular kg_totales automáticamente
        if self.medida == 'Chasis':
            if self.bruto and self.tara:
                self.kg_totales = self.bruto - self.tara
        else:
            if self.peso_unitario and self.cantidad:
                self.kg_totales = self.peso_unitario * self.cantidad
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Cosecha {self.fecha} - {self.finca} - {self.variedad}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.kg_totales is not None and self.kg_totales <= 0:
            raise ValidationError({'kg_totales': 'Los kg totales deben ser mayor a cero'})
    
    class Meta:
        verbose_name = "Registro de Cosecha"
        verbose_name_plural = "Registros de Cosecha"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),  # Consultas por fecha
            models.Index(fields=['finca']),  # Filtros por finca
            models.Index(fields=['variedad']),  # Filtros por variedad
            models.Index(fields=['destino']),  # Filtros por destino
            models.Index(fields=['comprador']),  # Filtros por comprador
            models.Index(fields=['origen']),  # Filtros por origen
            models.Index(fields=['fecha', 'finca']),  # Consultas combinadas
            models.Index(fields=['fecha', 'variedad']),  # Análisis por variedad
            models.Index(fields=['kg_totales']),  # Para agregaciones de peso
        ]

# nuevo modelo para análisis
class AnalisisPermission(models.Model):
    """Modelo dummy para permisos de análisis"""
    class Meta:
        managed = False
        permissions = [
            ("can_view_analisis_data", "Can view analysis dashboards"),
        ]

class ProduccionPermission(models.Model):
    """Modelo dummy para permisos de producción"""
    class Meta:
        managed = False
        permissions = [
            ("can_view_produccion_data", "Can view production data"),
        ]

# AGREGAR al final del archivo models.py, después de CompradorIngreso:

class FincaCosecha(models.Model):
    """Modelo para gestionar fincas personalizadas de cosecha"""
    nombre = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Finca de Cosecha"
        verbose_name_plural = "Fincas de Cosecha"
        ordering = ['nombre']

class CompradorCosecha(models.Model):
    """Modelo para gestionar compradores personalizados de cosecha"""
    nombre = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Comprador de Cosecha"
        verbose_name_plural = "Compradores de Cosecha"
        ordering = ['nombre']

class CultivoCosecha(models.Model):
    """Modelo para gestionar cultivos personalizados de cosecha"""
    nombre = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Cultivo de Cosecha"
        verbose_name_plural = "Cultivos de Cosecha"
        ordering = ['nombre']

class VariedadCosecha(models.Model):
    """Modelo para gestionar variedades personalizadas de cosecha"""
    nombre = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Variedad de Cosecha"
        verbose_name_plural = "Variedades de Cosecha"
        ordering = ['nombre']