from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
#URLs for main page
    path('api/parcelas/', views.parcelas_geojson, name='parcelas_geojson'),
#URLs for Administracion
    path('contabilidad/', views.contabilidad, name='contabilidad'),
    #URLs for Jornales
    path('administracion/jornales/cargar', views.cargar_jornal, name='cargar_jornal'),
    path('administracion/jornales/consultar', views.consultar_jornal, name='consultar_jornal'),
    path('administracion/jornales/exportar/csv', views.exportar_jornales_csv, name='exportar_jornales_csv'),
    #URLs for Movimientos
    #Egresos
    path('administracion/movimientos/cargar', views.cargar_movimiento, name='cargar_movimiento'), 
    path('administracion/movimientos/consultar', views.consultar_movimiento, name='consultar_movimiento'),
    path('administracion/movimientos/exportar/csv', views.exportar_movimientos_csv, name='exportar_movimientos_csv'),
    #APIs
    path('api/administracion/get-tasks/<str:classification>/', views.get_tasks_for_classification, name='get_tasks_for_classification'),
    path('api/administracion/get-classifications/<str:tipo>/', views.get_classifications_for_type, name='get_classifications_for_type'),
    #Ingresos
    path('administracion/ingresos/cargar', views.cargar_ingresos, name='cargar_ingresos'),
    path('administracion/ingresos/consultar', views.consultar_ingresos, name='consultar_ingresos'),
    path('administracion/ingresos/exportar/csv', views.exportar_ingresos_csv, name='exportar_ingresos_csv'),
#URLs for Producción
    path('produccion/', views.produccion, name='produccion'),
    # URLs para Riego y Fertilización
    path('produccion/riego/cargar/', views.cargar_riego, name='cargar_riego'),
    path('produccion/riego/consultar/', views.consultar_riego, name='consultar_riego'),
    path('produccion/riego/exportar/csv/', views.exportar_riegos_csv, name='exportar_riegos_csv'),
    # APIs 
    path('api/produccion/get-parrales/<str:cabezal>/', views.get_parrales_for_cabezal, name='get_parrales_for_cabezal'),
    path('api/produccion/get-valvulas/<str:cabezal>/<str:parral>/', views.get_valvulas_for_parral, name='get_valvulas_for_parral'),
#URLs for Analisis
    path('analisis/', views.analisis, name='analisis'),
    path('visualizacion/analisis/movimientos/', views.analisis_movimientos, name='analisis_movimientos'),
    # URL para la nueva API del gráfico de líneas
    path('api/visualizacion/movimientos/line-chart-data/', views.line_chart_data_api, name='line_chart_data_api'),
#URLs for Flujo de Caja
    path('flujo/flujo_anual/', views.flujo_anual, name='flujo_anual'),
    ]