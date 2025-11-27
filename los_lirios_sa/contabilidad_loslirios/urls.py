from django.urls import path, include
from . import views

# REEMPLAZAR estas líneas en urls.py (eliminar duplicados):

urlpatterns = [
    # Autenticación
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Página principal
    path('', views.main, name='main'),
    
    # URLs for main page
    path('api/parcelas/', views.parcelas_geojson, name='parcelas_geojson'),
    
    # URLs for Administracion
    path('contabilidad/', views.contabilidad, name='contabilidad'),
    
    # URLs for Movimientos - Egresos
    path('administracion/movimientos/cargar', views.cargar_movimiento, name='cargar_movimiento'), 
    path('administracion/movimientos/consultar', views.consultar_movimiento, name='consultar_movimiento'),
    path('administracion/movimientos/exportar/csv', views.exportar_movimientos_csv, name='exportar_movimientos_csv'),
    path('administracion/movimientos/editar/<int:id>/', views.editar_movimiento, name='editar_movimiento'),
    path('administracion/movimientos/eliminar/<int:id>/', views.eliminar_movimiento, name='eliminar_movimiento'),
    
    # APIs
    path('api/administracion/get-tasks/<str:classification>/', views.get_tasks_for_classification, name='get_tasks_for_classification'),
    path('api/administracion/get-classifications/<str:tipo>/', views.get_classifications_for_type, name='get_classifications_for_type'),
    path('api/ingresos/get-destinos/', views.get_destinos_ingresos, name='get_destinos_ingresos'),
    path('api/ingresos/get-compradores/', views.get_compradores_ingresos, name='get_compradores_ingresos'),
    path('api/ingresos/agregar-destino/', views.agregar_destino_ingreso, name='agregar_destino_ingreso'),
    path('api/ingresos/agregar-comprador/', views.agregar_comprador_ingreso, name='agregar_comprador_ingreso'),
    
    # Ingresos
    path('administracion/ingresos/cargar', views.cargar_ingresos, name='cargar_ingresos'),
    path('administracion/ingresos/consultar', views.consultar_ingresos, name='consultar_ingresos'),
    path('administracion/ingresos/exportar/csv', views.exportar_ingresos_csv, name='exportar_ingresos_csv'),
    path('administracion/ingresos/editar/<int:id>/', views.editar_ingreso, name='editar_ingreso'),
    path('administracion/ingresos/eliminar/<int:id>/', views.eliminar_ingreso, name='eliminar_ingreso'),
    
    # URLs for Producción
    path('produccion/', views.produccion, name='produccion'),
    
    # URLs for Jornales
    path('produccion/jornales/cargar', views.cargar_jornal, name='cargar_jornal'),
    path('produccion/jornales/consultar', views.consultar_jornal, name='consultar_jornal'),
    path('produccion/jornales/exportar/csv', views.exportar_jornales_csv, name='exportar_jornales_csv'),
    path('administracion/jornales/editar/<int:id>/', views.editar_jornal, name='editar_jornal'),
    path('administracion/jornales/eliminar/<int:id>/', views.eliminar_jornal, name='eliminar_jornal'),
    
    # URLs para Riego y Fertilización
    path('produccion/riego/cargar/', views.cargar_riego, name='cargar_riego'),
    path('produccion/riego/consultar/', views.consultar_riego, name='consultar_riego'),
    path('produccion/riego/exportar/csv/', views.exportar_riegos_csv, name='exportar_riegos_csv'),
    path('produccion/riego/editar/<int:id>/', views.editar_riego, name='editar_riego'),
    path('produccion/riego/eliminar/<int:id>/', views.eliminar_riego, name='eliminar_riego'),
    
    # APIs 
    path('api/produccion/get-parrales/<str:cabezal>/', views.get_parrales_for_cabezal, name='get_parrales_for_cabezal'),
    path('api/produccion/get-valvulas/<str:cabezal>/<str:parral>/', views.get_valvulas_for_parral, name='get_valvulas_for_parral'),
    
    # URLs para Cosecha
    path('produccion/cosecha/cargar/', views.cargar_cosecha, name='cargar_cosecha'),
    path('produccion/cosecha/consultar/', views.consultar_cosecha, name='consultar_cosecha'),
    path('produccion/cosecha/exportar/csv/', views.exportar_cosecha_csv, name='exportar_cosecha_csv'),
    path('produccion/cosecha/editar/<int:id>/', views.editar_cosecha, name='editar_cosecha'),
    path('produccion/cosecha/eliminar/<int:id>/', views.eliminar_cosecha, name='eliminar_cosecha'),
    
    # APIs para Cosecha
    path('api/cosecha/get-fincas/', views.get_fincas_cosecha, name='get_fincas_cosecha'),
    path('api/cosecha/get-compradores/', views.get_compradores_cosecha, name='get_compradores_cosecha'),
    path('api/cosecha/get-cultivos/', views.get_cultivos_cosecha, name='get_cultivos_cosecha'),
    path('api/cosecha/get-variedades/', views.get_variedades_cosecha, name='get_variedades_cosecha'),
    path('api/cosecha/agregar-finca/', views.agregar_finca_cosecha, name='agregar_finca_cosecha'),
    path('api/cosecha/agregar-comprador/', views.agregar_comprador_cosecha, name='agregar_comprador_cosecha'),
    path('api/cosecha/agregar-cultivo/', views.agregar_cultivo_cosecha, name='agregar_cultivo_cosecha'),
    path('api/cosecha/agregar-variedad/', views.agregar_variedad_cosecha, name='agregar_variedad_cosecha'),
    
    # URLs for Analisis
    path('analisis/', views.analisis, name='analisis'),
    path('visualizacion/analisis/movimientos/', views.analisis_movimientos, name='analisis_movimientos'),
    path('api/dashboard/kpis/', views.dashboard_kpis_api, name='dashboard_kpis_api'),
    path('api/visualizacion/movimientos/line-chart-data/', views.line_chart_data_api, name='line_chart_data_api'),
    
    # URLs for Flujo de Caja
    path('flujo/flujo_anual/', views.flujo_anual, name='flujo_anual'),
    path('analisis/flujo_anual/sueldos/', views.sueldos_flujo_anual, name='sueldos_flujo_anual'),
    
    # BÚSQUEDA AVANZADA Y EXPORTACIÓN
    path('administracion/busqueda-avanzada/movimientos/', views.busqueda_avanzada_movimientos, name='busqueda_avanzada_movimientos'),
    path('administracion/exportar/movimientos/excel/', views.exportar_movimientos_excel, name='exportar_movimientos_excel'),
    
    # APIs PARA TESTS (consolidadas)
    path('autocompletar/origen-movimiento/', views.autocompletar_origen_movimiento, name='autocompletar_origen_movimiento'),
    path('exportar/movimientos/excel/', views.exportar_movimientos_excel, name='exportar_movimientos_excel'),
    
    # ALIAS PARA CONSISTENCIA EN TESTS
    path('consultar/movimientos/', views.consultar_movimiento, name='consultar_movimientos'),
    path('consultar/ingresos/', views.consultar_ingresos, name='consultar_ingresos'),
    path('cargar/movimientos/', views.cargar_movimiento, name='cargar_movimientos'),
    path('cargar/ingresos/', views.cargar_ingresos, name='cargar_ingresos'),
]