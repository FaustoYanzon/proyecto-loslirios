class FormRegistroRiego(forms.ModelForm):
    # Definimos los campos que serán dinámicos
    cabezal = forms.ChoiceField(choices=[('', 'Seleccione Cabezal')] + [(c, c) for c in RIEGO_DATA.keys()])
    parral = forms.ChoiceField(choices=[('', 'Seleccione un Cabezal primero')])
    # CAMBIO: Usamos ChoiceField para un menú desplegable
    valvula_abierta = forms.ChoiceField(
        choices=[], 
        label="Válvula Abierta",
        required=True
    )

    class Meta:
        model = RegistroRiego
        # CAMBIO: Actualizamos el nombre del campo
        fields = [
            'cabezal', 'parral', 'valvula_abierta', 'inicio', 'fin',
            'fertilizante_nombre', 'fertilizante_litros', 'responsable'
        ]
        widgets = {
            'inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fertilizante_nombre': forms.TextInput(attrs={'placeholder': 'Ej: Urea'}),
            'fertilizante_litros': forms.NumberInput(attrs={'placeholder': '0.00'}),
            'responsable': forms.TextInput(attrs={'placeholder': 'Nombre del responsable'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        # La lógica para poblar los selects se mantiene, pero ahora para 'valvula_abierta'
        if self.data or self.instance.pk:
            cabezal = self.data.get('cabezal') or getattr(self.instance, 'cabezal', None)
            parral = self.data.get('parral') or getattr(self.instance, 'parral', None)

            if cabezal:
                parrales_choices = RIEGO_DATA.get(cabezal, {}).keys()
                self.fields['parral'].choices = [('', 'Seleccione Parral/Potrero')] + [(p, p) for p in parrales_choices]
            
            if cabezal and parral:
                valvulas_choices = RIEGO_DATA.get(cabezal, {}).get(parral, [])
                # CAMBIO: Actualizamos el campo 'valvula_abierta'
                self.fields['valvula_abierta'].choices = [('', 'Seleccione Válvula')] + [(v, v) for v in valvulas_choices]



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

    class FormConsultaRiego(forms.Form):
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
    cabezal = forms.ChoiceField(
        choices=[('', 'Todos')] + [(c, c) for c in RIEGO_DATA.keys()],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    parral = forms.ChoiceField(
        choices=[('', 'Todos')], # Se llenará con JS
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    responsable = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del responsable', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error('fecha_hasta', 'La fecha "Hasta" no puede ser anterior a la fecha "Desde".')
        return cleaned_data


class FormRegistroRiego(forms.ModelForm):
    # Definimos los campos que serán dinámicos
    cabezal = forms.ChoiceField(choices=[('', 'Seleccione Cabezal')] + [(c, c) for c in RIEGO_DATA.keys()])
    parral = forms.ChoiceField(choices=[('', 'Seleccione un Cabezal primero')])
    # CAMBIO: Usamos ChoiceField para un menú desplegable
    valvula_abierta = forms.ChoiceField(
        choices=[], 
        label="Válvula Abierta",
        required=True
    )

    class Meta:
        model = RegistroRiego
        # CAMBIO: Actualizamos el nombre del campo
        fields = [
            'cabezal', 'parral', 'valvula_abierta', 'inicio', 'fin',
            'fertilizante_nombre', 'fertilizante_litros', 'responsable'
        ]
        widgets = {
            'inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fertilizante_nombre': forms.TextInput(attrs={'placeholder': 'Ej: Urea'}),
            'fertilizante_litros': forms.NumberInput(attrs={'placeholder': '0.00'}),
            'responsable': forms.TextInput(attrs={'placeholder': 'Nombre del responsable'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        # La lógica para poblar los selects se mantiene, pero ahora para 'valvula_abierta'
        if self.data or self.instance.pk:
            cabezal = self.data.get('cabezal') or getattr(self.instance, 'cabezal', None)
            parral = self.data.get('parral') or getattr(self.instance, 'parral', None)

            if cabezal:
                parrales_choices = RIEGO_DATA.get(cabezal, {}).keys()
                self.fields['parral'].choices = [('', 'Seleccione Parral/Potrero')] + [(p, p) for p in parrales_choices]
            
            if cabezal and parral:
                valvulas_choices = RIEGO_DATA.get(cabezal, {}).get(parral, [])
                # CAMBIO: Actualizamos el campo 'valvula_abierta'
                self.fields['valvula_abierta'].choices = [('', 'Seleccione Válvula')] + [(v, v) for v in valvulas_choices]


{% extends "contabilidad_loslirios/main.html" %}
{% load static %}
{% block contenido %}
        {# Mensajes de Django (Toastify-js los leerá y los mostrará) #}
        {% if messages %}
            <ul class="messages mb-4 hidden"> {# Añade 'hidden' para que no se muestren dos veces #}
                {% for message in messages %}
                    <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
                {% endfor %}
            </ul>
        {% endif %}
        <div class="flex items-center mb-6">
            <a href="{% url 'produccion' %}" class="text-blue-600 hover:text-blue-800 flex items-center">
                <i class="fas fa-arrow-left mr-2"></i> Volver a Producción
            </a>
            <h1 class="text-2xl font-semibold text-gray-800 ml-4">Cargar Jornales</h1>
        </div>

        <form method="post" id="formulario-jornales">
            {% csrf_token %}
            {{ formset.management_form }}
            <table class="table-auto w-full" id="tabla-jornales">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Nombre Trabajador</th>
                        <th>Clasificación</th>
                        <th>Tarea</th>
                        <th>Detalle</th>
                        <th>Cantidad</th>
                        <th>Unidad Medida</th>
                        <th>Precio</th>
                        <th>Ubicación</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {% for form in formset %}
                    <tr class="formset-row">
                        {% for field in form.visible_fields %}
                            {% if field.name == "fecha" %}
                            <td>
                                {{ field }}
                                <button type="button" class="btn-copiar-fecha bg-gray-300 text-xs px-2 py-1 rounded ml-1" title="Copiar fecha anterior">⮌</button>
                            </td>
                            {% else %}
                            <td>{{ field }}</td>
                            {% endif %}
                        {% endfor %}
                        <td>
                            <button type="button" class="btn-eliminar bg-red-500 text-white px-2 py-1 rounded">Eliminar</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <button type="button" id="btn-agregar" class="bg-blue-600 text-white py-2 px-4 rounded-lg font-medium mb-4">
                <i class="fas fa-plus mr-2"></i>Agregar fila
            </button>
            <button type="submit" class="btn bg-green-600 text-white py-2 px-6 rounded-lg font-medium flex items-center">
                <i class="fas fa-save mr-2"></i>Cargar
            </button>
        </form>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // --- Función para actualizar el select de tareas según la clasificación ---
        function actualizarTareas(clasificacionSelect, tareaSelect) {
            const clasificacion = clasificacionSelect.value;
            if (!clasificacion) {
                tareaSelect.innerHTML = '<option value="">Seleccione una clasificación primero</option>';
                tareaSelect.disabled = true;
                return;
            }
            tareaSelect.innerHTML = '<option value="">Cargando...</option>';
            tareaSelect.disabled = true;
            fetch(`/api/administracion/get-tasks/${clasificacion}/`)
                .then(response => response.json())
                .then(data => {
                    tareaSelect.innerHTML = '';
                    tareaSelect.add(new Option('Seleccione una tarea', ''));
                    data.tasks.forEach(function(task) {
                        tareaSelect.add(new Option(task, task));
                    });
                    tareaSelect.disabled = false;
                })
                .catch(error => {
                    tareaSelect.innerHTML = '<option value="">Error al cargar tareas</option>';
                    tareaSelect.disabled = true;
                });
        }

        // --- Función para enlazar eventos a todos los selects de clasificación ---
        function bindClasificacionEvents() {
            document.querySelectorAll('select[name$="-clasificacion"]').forEach(function(clasificacionSelect) {
                const row = clasificacionSelect.closest('tr');
                const tareaSelect = row.querySelector('select[name$="-tarea"]');
                if (clasificacionSelect && tareaSelect) {
                    // Evita duplicar el evento
                    clasificacionSelect.onchange = null;
                    clasificacionSelect.addEventListener('change', function() {
                        actualizarTareas(clasificacionSelect, tareaSelect);
                    });
                    // Inicializa el select de tarea si hay valor preseleccionado
                    actualizarTareas(clasificacionSelect, tareaSelect);
                }
            });
        }

        // --- Inicializa los eventos al cargar la página ---
        bindClasificacionEvents();

        // --- Cuando agregas una fila, vuelve a enlazar los eventos ---
        document.getElementById('btn-agregar').addEventListener('click', function() {
            setTimeout(bindClasificacionEvents, 100); // Espera a que la fila se agregue
        });

        // --- También vuelve a enlazar los eventos al eliminar una fila ---
        document.getElementById('tabla-jornales').addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-eliminar')) {
                setTimeout(bindClasificacionEvents, 100);
            }
        });
    });

    // --- Dinámica de agregar/eliminar filas ---
    document.addEventListener('DOMContentLoaded', function() {
        const tabla = document.getElementById('tabla-jornales').getElementsByTagName('tbody')[0];
        const btnAgregar = document.getElementById('btn-agregar');
        const totalForms = document.getElementById('id_form-TOTAL_FORMS');

        btnAgregar.addEventListener('click', function() {
            // Clona la última fila
            const filas = tabla.querySelectorAll('.formset-row');
            const ultimaFila = filas[filas.length - 1];
            const nuevaFila = ultimaFila.cloneNode(true);

            // Limpia los valores de los inputs
            nuevaFila.querySelectorAll('input, select, textarea').forEach(function(input) {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            });

            // Actualiza los atributos name e id para el formset
            const formIndex = parseInt(totalForms.value);
            nuevaFila.querySelectorAll('input, select, textarea').forEach(function(input) {
                if (input.name) {
                    input.name = input.name.replace(/form-(\d+)-/, `form-${formIndex}-`);
                }
                if (input.id) {
                    input.id = input.id.replace(/form-(\d+)-/, `form-${formIndex}-`);
                }
            });

            tabla.appendChild(nuevaFila);
            totalForms.value = formIndex + 1;
        });

        // Eliminar fila
        tabla.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-eliminar')) {
                const filas = tabla.querySelectorAll('.formset-row');
                if (filas.length > 1) {
                    e.target.closest('.formset-row').remove();
                    totalForms.value = filas.length - 1;
                }
            }
        });
    });
    </script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('tabla-jornales').addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-copiar-fecha')) {
            const filaActual = e.target.closest('tr');
            const filas = Array.from(document.querySelectorAll('#tabla-jornales .formset-row'));
            const idx = filas.indexOf(filaActual);
            if (idx > 0) {
                const fechaAnterior = filas[idx - 1].querySelector('input[name$="-fecha"]').value;
                filaActual.querySelector('input[name$="-fecha"]').value = fechaAnterior;
            }
        }
    });
});
</script>
<style>
    #tabla-jornales input,
    #tabla-jornales select,
    #tabla-jornales textarea {
        max-width: 140px;
        min-width: 80px;
        width: 120px;
        box-sizing: border-box;
    }
    #tabla-jornales th, #tabla-jornales td {
        padding: 4px;
    }
</style>
{% endblock %}



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

{% extends "contabilidad_loslirios/main.html" %}
{% load static %}
{% block titulo %}Cargar Movimiento - Los Lirios SA{% endblock titulo %}
{% block contenido %}
        {# Mensajes de Django (Toastify-js los leerá y los mostrará) #}
        {% if messages %}
            <ul class="messages mb-4 hidden"> 
                {% for message in messages %}
                    <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
                {% endfor %}
            </ul>
        {% endif %}
        <div class="flex items-center mb-6">
            <a href="{% url 'contabilidad' %}" class="text-blue-600 hover:text-blue-800 flex items-center">
                <i class="fas fa-arrow-left mr-2"></i> Volver a Administracion
            </a>
            <h1 class="text-2xl font-semibold text-gray-800 ml-4">Cargar Ingreso</h1>
        </div>

        
        <form method="POST" class="bg-white p-8 rounded-lg shadow-md" id="movimiento-form">
            {% csrf_token %} 

            {% if errores_carga %}
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                    <strong class="font-bold">¡Error al guardar!</strong>
                    <span class="block sm:inline">Por favor, corrija los siguientes errores:</span>
                    <ul class="mt-2 list-disc list-inside">
                        {% for field, errors in errores_carga.items %}
                            <li>{{ field }}: {{ errors|join:", " }}</li>
                        {% endfor %}
                        {% if formulario.non_field_errors %}
                            {% for error in formulario.non_field_errors %}
                                <li>{{ error }}</li>
                            {% endfor %}
                        {% endif %}
                    </ul>
                </div>
            {% endif %}

                <div class="flex flex-col md:flex-row gap-6">
                    <fieldset class="border p-4 rounded-md flex-1">
                        {# Campo Fecha #}
                        <div>
                            <label for="{{ formulario.fecha.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.fecha.label }}</label>
                            {{ formulario.fecha }}
                            {% if formulario.fecha.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.fecha.errors }}</p>
                            {% endif %}
                        </div>
                        {# Campo Origen #}
                        <div>
                            <label for="{{ formulario.origen.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.origen.label }}</label>
                            {{ formulario.origen }}
                            {% if formulario.origen.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.origen.errors }}</p>
                            {% endif %}
                        </div>
                        {# Campo Finca #}
                        <div>
                            <label for="{{ formulario.finca.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.finca.label }}</label>
                            {{ formulario.finca }}
                            {% if formulario.finca.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.finca.errors }}</p>
                            {% endif %}
                        </div>
                    </fieldset>

                    <fieldset class="border p-4 rounded-md flex-1">
                        {# Campo Tipo #}
                        <div>
                            <label for="{{ formulario.tipo.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.tipo.label }}</label>
                            {{ formulario.tipo }}
                            {% if formulario.tipo.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.tipo.errors }}</p>
                            {% endif %}
                        </div>
                        {# Campo Clasificacion #}
                        <div>
                            <label for="{{ formulario.clasificacion.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.clasificacion.label }}</label>
                            {{ formulario.clasificacion }}
                            {% if formulario.clasificacio.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.clasificacion.errors }}</p>
                            {% endif %}
                        </div>
                        {# Campo Detalle #}
                        <div>
                            <label for="{{ formulario.detalle.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.detalle.label }}</label>
                            {{ formulario.detalle }}
                            {% if formulario.detalle.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.detalle.errors }}</p>
                            {% endif %}
                        </div>
                    </fieldset>

                    <fieldset class="border p-4 rounded-md flex-1">
                        {# Campo Monto #}
                        <div>
                            <label for="{{ formulario.monto.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.monto.label }}</label>
                            {{ formulario.monto }}
                            {% if formulario.monto.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.monto.errors }}</p>
                            {% endif %}
                        </div>
                        {# Campo Moneda #}
                        <div>
                            <label for="{{ formulario.moneda.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.moneda.label }}</label>
                            {{ formulario.moneda }}
                            {% if formulario.moneda.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.moneda.errors }}</p>
                            {% endif %}
                        </div>
                        {# Campo Forma_Pago #}
                        <div>
                            <label for="{{ formulario.forma_pago.id_for_label }}" class="block text-gray-700 text-sm font-bold mb-2">{{ formulario.forma_pago.label }}</label>
                            {{ formulario.forma_pago }}
                            {% if formulario.forma_pago.errors %}
                                <p class="text-red-500 text-xs italic">{{ formulario.forma_pago.errors }}</p>
                            {% endif %}
                        </div>
                    </fieldset>
                </div>
            </div>
            <div class="mt-6 flex justify-center space-x-4">
                <button type="submit" class="btn bg-green-600 hover:bg-green-700 text-white py-2 px-6 rounded-lg font-medium flex items-center">
                    <i class="fas fa-save mr-2"></i> Guardar Movimientos
                </button>
            </div>
        </form>
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const tipoSelect = document.getElementById('{{ formulario.tipo.id_for_label }}');
            const clasificacionSelect = document.getElementById('{{ formulario.clasificacion.id_for_label }}');

            tipoSelect.addEventListener('change', function() {
                const tipo = this.value;
                clasificacionSelect.innerHTML = '<option value="">Cargando...</option>';

                if (!tipo) {
                    clasificacionSelect.innerHTML = '<option value="">Seleccione un Tipo</option>';
                    return;
                }

                const url = `{% url 'get_classifications_for_type' '0' %}`.replace('0', tipo);
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        clasificacionSelect.innerHTML = '<option value="">---------</option>';
                        data.classifications.forEach(c => {
                            clasificacionSelect.add(new Option(c, c));
                        });
                    });
            });
        });
        </script>
{% endblock contenido %}



