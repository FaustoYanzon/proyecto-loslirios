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
    
    class Meta:
        verbose_name = "Registro de Trabajo"
        verbose_name_plural = "Registros de Trabajo"
        # Permisos personalizados para el modelo registro_trabajo
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

    class Meta:
        verbose_name = "Movimiento Financiero"
        verbose_name_plural = "Movimientos Financieros"
        ordering = ['-fecha'] 
        permissions = [
            ("can_view_movimientos", "Can view all financial movements"),
            ("can_add_movimientos", "Can add new financial movements"),
            ("can_export_movimientos", "Can export financial movements data"),
        ]
#Modelo Movimiento Financiero Ingresos
class IngresoFinanciero(models.Model):
    id_ingreso = models.AutoField(primary_key=True)
    fecha = models.DateField()
    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES)   
    finca = models.CharField(max_length=20, choices=FINCA_CHOICES)
    detalle = models.TextField(blank=True, null=True) 
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES)
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES)

    def __str__(self):
        return f"{self.fecha} | {self.finca} - {self.moneda} {self.monto}"

    class Meta:
        verbose_name = "Ingreso Financiero"
        verbose_name_plural = "Ingresos Financieros"
        ordering = ['-fecha'] 
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

    class Meta:
        verbose_name = "Registro de Riego"
        verbose_name_plural = "Registros de Riego"
        ordering = ['-inicio']
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
    
    class Meta:
        verbose_name = "Registro de Cosecha"
        verbose_name_plural = "Registros de Cosecha"
        ordering = ['-fecha']

