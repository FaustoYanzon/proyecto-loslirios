# contabilidad_loslirios/management/commands/importar_parcelas.py

import csv
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from django.conf import settings
from contabilidad_loslirios.models import Parcela
import os
import re

class Command(BaseCommand):
    help = 'Importa los datos de las parcelas desde los archivos KML y CSV'

    def handle(self, *args, **options):
        # --- 1. LEER LOS DATOS DESCRIPTIVOS DEL CSV ---
        self.stdout.write("Leyendo datos desde parcelas_data.csv...")
        
        datos_descriptivos = {}
        csv_path = os.path.join(settings.BASE_DIR, 'contabilidad_loslirios', 'parcelas_data.csv')
        
        try:
            with open(csv_path, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    # Usamos .lower() para hacer la búsqueda insensible a mayúsculas/minúsculas
                    nombre_limpio = row['PARRALES/POTREROS'].strip().lower()
                    datos_descriptivos[nombre_limpio] = {
                        'variedad': row['VARIEDAD'].strip() if row['VARIEDAD'].strip() != '-' else None,
                        'superficie_ha': float(row['SUPERFICIE'].replace(',', '.')) if row['SUPERFICIE'].strip() and row['SUPERFICIE'].strip() != '-' else None,
                        'cabezal_riego': row['CABEZAL'].strip() if row['CABEZAL'].strip() and row['CABEZAL'].strip() != '-' else None,
                    }
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: No se encontró el archivo en {csv_path}"))
            return
            
        self.stdout.write(self.style.SUCCESS(f"Se encontraron {len(datos_descriptivos)} registros en el CSV."))

        # --- 2. LEER LOS DATOS GEOGRÁFICOS DEL KML ---
        self.stdout.write("Leyendo geometrías desde Los Lirios.kml...")
        kml_path = os.path.join(settings.BASE_DIR, 'contabilidad_loslirios', 'Los Lirios.kml')

        try:
            tree = ET.parse(kml_path)
            root = tree.getroot()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: No se encontró el archivo en {kml_path}"))
            return

        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        # --- 3. PROCESAR Y GUARDAR EN LA BASE DE DATOS ---
        
        # **MEJORA:** Creamos un mapa para los nombres especiales
        special_name_map = {
            'parral bond. nuevo': 'pbn',
            'parral bond. viejo': 'pbv',
            'parral syr-rg': 'psy-rg',
            'parral sult.': 'psul',
            'pasero 1': '20',  # Mapea 'Pasero 1' del KML a la clave '20' del CSV
            'pasero 2': '19'   # Agregado por si acaso
        }

        contador_parcelas = 0
        for placemark in root.findall('.//kml:Placemark', ns):
            nombre_kml_element = placemark.find('kml:name', ns)
            if nombre_kml_element is None:
                continue

            # Limpiamos y pasamos a minúsculas el nombre del KML
            nombre_kml = re.sub(r'\s+', ' ', nombre_kml_element.text).strip().lower()
            
            # Buscamos la clave para nuestro diccionario de datos
            key_busqueda = special_name_map.get(nombre_kml)
            if not key_busqueda:
                # Si no es un nombre especial, usamos la lógica anterior
                key_busqueda = nombre_kml.replace('parral ', '').replace('potrero ', '')
                if '-' in key_busqueda:
                    key_busqueda = key_busqueda.split('-')[0]

            datos = datos_descriptivos.get(key_busqueda)

            if not datos:
                self.stdout.write(self.style.WARNING(f"ADVERTENCIA: No se encontraron datos para la parcela '{nombre_kml}' (buscando como '{key_busqueda}')."))
                datos = {}

            coordinates_element = placemark.find('.//kml:coordinates', ns)
            if coordinates_element is not None:
                coords_str = coordinates_element.text.strip()
                coords_list = []
                for point in coords_str.split(' '):
                    if ',' in point:
                        lon, lat, alt = point.split(',')
                        coords_list.append([float(lat), float(lon)])
                
                # Usamos el nombre original del KML (capitalizado) para guardarlo
                nombre_final = nombre_kml_element.text.strip()
                obj, created = Parcela.objects.update_or_create(
                    nombre=nombre_final,
                    defaults={
                        'variedad': datos.get('variedad'),
                        'superficie_ha': datos.get('superficie_ha'),
                        'cabezal_riego': datos.get('cabezal_riego'),
                        'coordenadas': coords_list,
                    }
                )
                contador_parcelas += 1

        self.stdout.write(self.style.SUCCESS(f"\n¡Proceso de actualización completado! Se revisaron {contador_parcelas} parcelas."))