from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm
#Create forms here

#Administration

#Model for daily work
#Options for choices in the form
unidades_de_medida = [
    ('Días', 'Días'),
    ('Plantas', 'Plantas'),
    ('Melgas', 'Melgas'),
    ('Camellón', 'Camellón'),
    ('Metros', 'Metros'),
    ('Fichas', 'Fichas'),
    ('Vin Grande', 'Vin Grande'),
    ('Vin Pequeño', 'Vin Pequeño'),
    ('Otros', 'Otros'),
]
TAREAS_POR_CLASIFICACION = {
    'Verano': ['Jornal Comun', 'Cosecha', 'Tractor Cosecha', 'Pasero', 'Levantar Pasa', 'Control Cosecha', 'Amontonar Pasa', 'Otros'],
    'Invierno': ['Jornal Comun', 'Poda', 'Atada', 'Tejido', 'Otros'],
    'Primavera': ['Jornal Comun', 'Verde', 'Brote', 'Raleo', 'Polainas', 'Descole', 'Otros'],
    'Otoño': ['Jornal Comun', 'Murones', 'Otros'],
    'General': ['Jornal Comun', 'Tractor Comun', 'Riego', 'Const. Parral', 'Mochila', 'Limpieza Acequia', 'Rastrillar Pasa', 'Anchada', 'Zanjeo', 'Otros'],
}
#Form for daily work upload
class FormRegistroTrabajo(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    unidad_medida = forms.ChoiceField(choices=unidades_de_medida)
    tarea = forms.ChoiceField(choices=[('', 'Seleccione una clasificación primero')])

    class Meta:
        model = registro_trabajo
        fields = [
            'fecha', 'nombre_trabajador', 'clasificacion', 'tarea', 'detalle',
            'cantidad', 'unidad_medida', 'precio', 'ubicacion'
        ]
        widgets = {
            'nombre_trabajador': forms.TextInput(attrs={'placeholder': 'Nombre del Empleado'}),
            'clasificacion': forms.Select(attrs={'class': 'form-control'}),
            'tarea': forms.Select(attrs={'class': 'form-control'}),
            'detalle': forms.TextInput(attrs={'placeholder': 'Detalles adicionales de la tarea'}),
            'cantidad': forms.NumberInput(attrs={'placeholder': 'Cantidad', 'step': '0.5'}),
            'precio': forms.NumberInput(attrs={'placeholder': 'Precio', 'step': '1'}),
            'ubicacion': forms.TextInput(attrs={'placeholder': 'Ubicación'}),
        }
        labels = {
            'fecha': 'Fecha',
            'precio': 'Precio',
            'cantidad': 'Cantidad',
            'nombre_trabajador': 'Nombre Empleado',
            'clasificacion': 'Clasificación',
            'tarea': 'Tarea Realizada',
            'detalle': 'Detalles',
            'unidad_medida': 'Unidad de Medida',
            'ubicacion': 'Ubicación',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Actualiza las opciones de tarea según la clasificación seleccionada
        clasificacion = self.data.get(self.add_prefix('clasificacion')) or getattr(self.instance, 'clasificacion', None)
        if clasificacion in TAREAS_POR_CLASIFICACION:
            self.fields['tarea'].choices = [(t, t) for t in TAREAS_POR_CLASIFICACION[clasificacion]]
        else:
            self.fields['tarea'].choices = [('', 'Seleccione una clasificación primero')]

        # Aplica clases y atributos a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['fecha'].widget.attrs.update({'type': 'date'})
        self.fields['cantidad'].widget.attrs.update({'step': '0.5'})
        self.fields['precio'].widget.attrs.update({'step': '1'})
#Form for consult daily work
class FormConsultaJornal(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha Desde'
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha Hasta'
    )
    nombre_trabajador = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del Empleado','class': 'form-control'}),
        label='Nombre del Trabajador'
    )
    clasificacion = forms.ChoiceField(
        choices=[('', 'Todas')] + list(CLASIFICACION_CHOICES), 
        label='Clasificación',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tarea = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas')], 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tarea Realizada'
    )
    detalle = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Buscar en detalles', 'class': 'form-control'}),
        label='Detalle'
    )
    ubicacion = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ubicación', 'class': 'form-control'}),
        label='Ubicación'
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error('fecha_hasta', 'La fecha "Hasta" no puede ser anterior a la fecha "Desde".')
        return cleaned_data



#Model for financial movements
#Options for choices in the form
CLASIFICACIONES_POR_TIPO = {
    'Sueldos Personal': ['Gerenciales', 'Encargados', 'Obreros', 'Contador', 'Abogado', 'Administrador','VEP', 'Otros'],
    'Produccion': ['Fertilizantes', 'Agroquímicos', 'Otros'],
    'Inversion': ['Movilidad', 'Infraestructura', 'Riego', 'Maquinaria','Parral', 'Otros'],
    'Repuestos y Reparaciones': ['Movilidad', 'Maquinaria', 'Riego','Infraestructura', 'Otros'],
    'Insumos Varios': ['Indumentaria', 'Herramientas', 'Combustibles', 'Otros'],
    'Impuestos o Servicios': [ 'Hidraulica', 'Rentas', 'Municipal', 'Otros'],
    'Energia': ['Riego','Domiciliaria', 'Otros'],
}
#Form for financial movements upload
class FormMovimientoFinanciero(forms.ModelForm):
    clasificacion = forms.ChoiceField(choices=[('', 'Seleccione un Tipo primero')])
    
    class Meta:
        model = MovimientoFinanciero
        fields = ['fecha', 'origen', 'finca', 'tipo', 'clasificacion', 'detalle', 'monto', 'moneda', 'forma_pago']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'detalle': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Detalles'}),
            'monto': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'tipo' in self.data:
            try:
                tipo_id = self.data.get('tipo')
                self.fields['clasificacion'].choices = [(c, c) for c in CLASIFICACIONES_POR_TIPO[tipo_id]]
            except (ValueError, TypeError, KeyError):
                self.fields['clasificacion'].choices = [('', 'Seleccione un tipo válido')]
        elif self.instance.pk:
            try:
                self.fields['clasificacion'].choices = [(c, c) for c in CLASIFICACIONES_POR_TIPO[self.instance.tipo]]
            except KeyError:
                self.fields['clasificacion'].choices = [('', 'Tipo no válido')]

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
#Form for consult financial movements 
class FormConsultaMovimiento(forms.Form):
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    
    origen = forms.ChoiceField(choices=[('', 'Todos')] + ORIGEN_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    finca = forms.ChoiceField(choices=[('', 'Todas')] + FINCA_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    tipo = forms.ChoiceField(choices=[('', 'Todos')] + TIPO_MOVIMIENTO_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    clasificacion = forms.ChoiceField(choices=[('', 'Todas')], required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    moneda = forms.ChoiceField(choices=[('', 'Todas')] + MONEDA_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    forma_pago = forms.ChoiceField(choices=[('', 'Todas')] + FORMA_PAGO_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error('fecha_hasta', 'La fecha "Hasta" no puede ser anterior a la fecha "Desde".')
        return cleaned_data

#Form for financial incomes upload
class FormIngresoFinanciero(forms.ModelForm):
    class Meta:
        model = IngresoFinanciero
        fields = [
            'fecha',
            'origen', 
            'destino',
            'comprador',
            'forma_pago',
            'forma',
            'banco',
            'numero_cheque', 
            'fecha_pago',
            'monto',
            'moneda'
        ]
        
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'origen': forms.Select(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seleccione o escriba un destino'
            }),
            'comprador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seleccione o escriba un comprador'
            }),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'forma': forms.Select(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del banco'
            }),
            'numero_cheque': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de cheque'
            }),
            'fecha_pago': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'moneda': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'attrs'):
                field.widget.attrs = {}
            field.widget.attrs.update({'class': 'form-control'})
            
        # Hacer campos condicionales no requeridos inicialmente
        self.fields['banco'].required = False
        self.fields['numero_cheque'].required = False
        self.fields['fecha_pago'].required = False

    def clean(self):
        cleaned_data = super().clean()
        forma_pago = cleaned_data.get('forma_pago')
        banco = cleaned_data.get('banco')
        numero_cheque = cleaned_data.get('numero_cheque')
        fecha_pago = cleaned_data.get('fecha_pago')
        
        # Validar campos obligatorios para Cheque/Echeque
        if forma_pago in ['Cheque', 'Echeque']:
            if not banco:
                raise forms.ValidationError({'banco': 'Este campo es obligatorio cuando la forma de pago es Cheque o Echeque.'})
            if not numero_cheque:
                raise forms.ValidationError({'numero_cheque': 'Este campo es obligatorio cuando la forma de pago es Cheque o Echeque.'})
            if not fecha_pago:
                raise forms.ValidationError({'fecha_pago': 'Este campo es obligatorio cuando la forma de pago es Cheque o Echeque.'})
        
        return cleaned_data

#Form for consult financial incomes
class FormConsultaIngresos(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha Desde'
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha Hasta'
    )
    origen = forms.ChoiceField(
        choices=[('', 'Todos')] + ORIGEN_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Origen'
    )
    destino = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar destino...'
        }),
        label='Destino'
    )
    comprador = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar comprador...'
        }),
        label='Comprador'
    )
    forma_pago = forms.ChoiceField(
        choices=[('', 'Todas')] + FORMA_PAGO_INGRESOS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Forma de Pago'
    )
    moneda = forms.ChoiceField(
        choices=[('', 'Todas')] + MONEDA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Moneda'
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error('fecha_hasta', 'La fecha "Hasta" no puede ser anterior a la fecha "Desde".')
        return cleaned_data


#Forms for analisis dashboard:
#Form for analisis jornales dashboard:
class FormFiltroDashboardJornales(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha Desde'
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha Hasta'
    )
    clasificacion = forms.MultipleChoiceField(
        choices=CLASIFICACION_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple, # Un widget de checkboxes es ideal para filtros
        label='Temporada'
    )
    tarea = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Tarea'
    )
    ubicacion = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Ubicación'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tarea'].choices = [(t, t) for t in registro_trabajo.objects.values_list('tarea', flat=True).distinct().order_by('tarea')]
        self.fields['ubicacion'].choices = [(u, u) for u in registro_trabajo.objects.values_list('ubicacion', flat=True).distinct().order_by('ubicacion')]
#Form for analisis financial movements dashboard:
class FormFiltroDashboardMovimientos(forms.Form):
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    
    origen = forms.MultipleChoiceField(choices=ORIGEN_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    finca = forms.MultipleChoiceField(choices=FINCA_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    tipo = forms.MultipleChoiceField(choices=TIPO_MOVIMIENTO_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    
    # Este se llenará con JavaScript
    clasificacion = forms.MultipleChoiceField(choices=[], required=False, widget=forms.CheckboxSelectMultiple)
    
    moneda = forms.MultipleChoiceField(choices=MONEDA_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    forma_pago = forms.MultipleChoiceField(choices=FORMA_PAGO_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_classifications = MovimientoFinanciero.objects.values_list('clasificacion', flat=True).distinct().order_by('clasificacion')
        self.fields['clasificacion'].choices = [(c, c) for c in all_classifications]



#Production
#Model for Irrigation and Fertilization
RIEGO_DATA = {
    '1': {'Sult.': ['1', '2', '3', '4'], '9': ['1', '2'], '4': ['1', '2'], '5': ['1', '2'], '2': ['1', '2']},
    '2': {'10': ['1', '2', '3'], '6': ['1', '2', '3', '4'], '2': ['1'], '11': ['1', '2', '3', '4'], '7': ['1', '2', '3', '4']},
    '3': {'16': ['1', '2'], '13': ['1', '2', '3'], '15': ['1', '2'], '14': ['1', '2', '3'], '21': ['1', '2', '3', '4'], '12': ['1', '2', '3']},
    '4': {'8': ['1', '2', '3'], 'SYR-RG': ['1', '2', '3'], 'Bond. Viejo': ['1', '2'], 'Bond. Nuevo': ['1', '2'], '3': ['1', '2']}
}
# Form for Irrigation and Fertilization upload
class FormRegistroRiego(forms.ModelForm):
    class Meta:
        model = RegistroRiego
        fields = [
            'inicio', 'fin', 'cabezal', 'parral', 'valvula_abierta',
            'fertilizante_nombre', 'fertilizante_litros', 'responsable'
        ]
        widgets = {
            'inicio': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'fin': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'fertilizante_nombre': forms.TextInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre del fertilizante (opcional)'
            }),
            'fertilizante_litros': forms.NumberInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre del responsable'
            })
        }
        labels = {
            'inicio': 'Fecha y Hora de Inicio',
            'fin': 'Fecha y Hora de Fin',
            'cabezal': 'Cabezal de Riego',
            'parral': 'Parral/Potrero',
            'valvula_abierta': 'Válvula Abierta',
            'fertilizante_nombre': 'Fertilizante (Opcional)',
            'fertilizante_litros': 'Litros de Fertilizante',
            'responsable': 'Responsable'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Definir los campos dinámicos con las clases CSS
        self.fields['cabezal'] = forms.ChoiceField(
            choices=[('', 'Seleccione Cabezal')] + [(c, c) for c in RIEGO_DATA.keys()],
            required=True,
            widget=forms.Select(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            label='Cabezal de Riego'
        )
        
        self.fields['parral'] = forms.ChoiceField(
            choices=[('', 'Seleccione un Cabezal primero')],
            required=True,
            widget=forms.Select(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            label='Parral/Potrero'
        )
        
        self.fields['valvula_abierta'] = forms.ChoiceField(
            choices=[('', 'Seleccione Válvula')],
            required=True,
            widget=forms.Select(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            label='Válvula Abierta'
        )

        # Lógica para poblar los selects dinámicamente
        if self.data:
            cabezal = self.data.get('cabezal')
            parral = self.data.get('parral')

            if cabezal and cabezal in RIEGO_DATA:
                parrales_choices = list(RIEGO_DATA[cabezal].keys())
                self.fields['parral'].choices = [('', 'Seleccione Parral/Potrero')] + [(p, p) for p in parrales_choices]
            
            if cabezal and parral and cabezal in RIEGO_DATA and parral in RIEGO_DATA[cabezal]:
                valvulas_choices = RIEGO_DATA[cabezal][parral]
                self.fields['valvula_abierta'].choices = [('', 'Seleccione Válvula')] + [(v, v) for v in valvulas_choices]

        elif self.instance.pk:
            # Si estamos editando un registro existente
            cabezal = getattr(self.instance, 'cabezal', None)
            parral = getattr(self.instance, 'parral', None)

            if cabezal and cabezal in RIEGO_DATA:
                parrales_choices = list(RIEGO_DATA[cabezal].keys())
                self.fields['parral'].choices = [('', 'Seleccione Parral/Potrero')] + [(p, p) for p in parrales_choices]
            
            if cabezal and parral and cabezal in RIEGO_DATA and parral in RIEGO_DATA[cabezal]:
                valvulas_choices = RIEGO_DATA[cabezal][parral]
                self.fields['valvula_abierta'].choices = [('', 'Seleccione Válvula')] + [(v, v) for v in valvulas_choices]

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('inicio')
        fin = cleaned_data.get('fin')
        cabezal = cleaned_data.get('cabezal')
        parral = cleaned_data.get('parral')
        valvula_abierta = cleaned_data.get('valvula_abierta')
        
        # Validación de fechas
        if inicio and fin and fin <= inicio:
            raise forms.ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
        
        # Validación de cabezal
        if cabezal and cabezal not in RIEGO_DATA:
            raise forms.ValidationError('Cabezal no válido.')
            
        # Validación de parral
        if cabezal and parral and parral not in RIEGO_DATA.get(cabezal, {}):
            raise forms.ValidationError('Parral no válido para el cabezal seleccionado.')
            
        # Validación de válvula
        if cabezal and parral and valvula_abierta:
            valid_valvulas = RIEGO_DATA.get(cabezal, {}).get(parral, [])
            if valvula_abierta not in valid_valvulas:
                raise forms.ValidationError('Válvula no válida para el parral seleccionado.')
            
        return cleaned_data
#Form for consult Irrigation and Fertilization
class FiltrosRiegoForm(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Fecha Desde'
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Fecha Hasta'
    )
    cabezal = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')],  # Las opciones se cargan dinámicamente en la vista
        widget=forms.Select(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Cabezal'
    )
    parral = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')],  # Las opciones se cargan dinámicamente en la vista
        widget=forms.Select(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Parral/Potrero'
    )
    responsable = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Buscar responsable...'
        }),
        label='Responsable'
    )


#Model for Harvest Records
# Form for Cosecha upload
class RegistroCosechaForm(forms.ModelForm):
    class Meta:
        model = RegistroCosecha
        fields = [
            'fecha', 'origen', 'finca', 'destino', 'comprador', 'cultivo',
            'parral_potrero', 'variedad', 'remito', 'ciu', 'medida', 
            'peso_unitario', 'cantidad', 'bruto', 'tara'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'origen': forms.Select(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'finca': forms.TextInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'list': 'finca-list'
            }),
            'destino': forms.Select(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'comprador': forms.TextInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'list': 'comprador-list'
            }),
            'cultivo': forms.TextInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'list': 'cultivo-list'
            }),
            'parral_potrero': forms.TextInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'variedad': forms.TextInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'list': 'variedad-list'
            }),
            'remito': forms.TextInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'ciu': forms.NumberInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'medida': forms.Select(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'id': 'id_medida'
            }),
            'peso_unitario': forms.NumberInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1'
            }),
            'bruto': forms.NumberInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'tara': forms.NumberInput(attrs={
                'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
        }
#Form for Consultin Cosecha
class FiltrosCosechaForm(forms.Form):
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Fecha Inicio'
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Fecha Fin'
    )
    origen = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + ORIGEN_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    finca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Buscar finca...'
        })
    )
    destino = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + DESTINO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    comprador = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Buscar comprador...'
        })
    )
    variedad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Buscar variedad...'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_fin', 'La fecha "Fin" no puede ser anterior a la fecha "Inicio".')
        return cleaned_data

#Custom Login Form
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 w-full',
            'placeholder': 'Usuario',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 w-full',
            'placeholder': 'Contraseña'
        })
    )

