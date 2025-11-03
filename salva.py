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
