#!/usr/bin/env python3
"""
Health Check Script para Los Lirios SA
Verifica el estado de todos los componentes del sistema
"""

import requests
import psutil
import os
import sys
import json
from datetime import datetime
import logging

# Configuración
HEALTH_CHECK_URL = "http://localhost:8000/health/"
LOG_FILE = "/var/log/los_lirios/health_check.log"
ALERT_THRESHOLD = {
    'cpu': 85,      # % CPU
    'memory': 85,   # % Memoria
    'disk': 90,     # % Disco
    'response_time': 5000  # ms
}

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_system_resources():
    """Verificar recursos del sistema"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'status': 'OK' if cpu_percent < ALERT_THRESHOLD['cpu'] else 'WARNING'
            },
            'memory': {
                'percent': memory.percent,
                'available': memory.available // (1024**3),  # GB
                'status': 'OK' if memory.percent < ALERT_THRESHOLD['memory'] else 'WARNING'
            },
            'disk': {
                'percent': disk.percent,
                'free': disk.free // (1024**3),  # GB
                'status': 'OK' if disk.percent < ALERT_THRESHOLD['disk'] else 'WARNING'
            }
        }
    except Exception as e:
        logging.error(f"Error verificando recursos del sistema: {e}")
        return None

def check_application_health():
    """Verificar estado de la aplicación"""
    try:
        start_time = datetime.now()
        response = requests.get(HEALTH_CHECK_URL, timeout=10)
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'status_code': response.status_code,
            'response_time': response_time,
            'status': 'OK' if response.status_code == 200 and response_time < ALERT_THRESHOLD['response_time'] else 'ERROR'
        }
    except Exception as e:
        logging.error(f"Error verificando aplicación: {e}")
        return {
            'status_code': 0,
            'response_time': 0,
            'status': 'ERROR',
            'error': str(e)
        }

def check_database():
    """Verificar conexión a la base de datos"""
    try:
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'los_lirios_sa.settings')
        django.setup()
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            
        return {'status': 'OK', 'connection': True}
    except Exception as e:
        logging.error(f"Error verificando base de datos: {e}")
        return {'status': 'ERROR', 'connection': False, 'error': str(e)}

def check_services():
    """Verificar servicios del sistema"""
    services = ['gunicorn-los-lirios', 'nginx', 'redis-server']
    results = {}
    
    for service in services:
        try:
            result = os.system(f'systemctl is-active {service} > /dev/null 2>&1')
            results[service] = {
                'status': 'OK' if result == 0 else 'ERROR',
                'active': result == 0
            }
        except Exception as e:
            results[service] = {'status': 'ERROR', 'active': False, 'error': str(e)}
    
    return results

def generate_report():
    """Generar reporte completo de salud"""
    timestamp = datetime.now().isoformat()
    
    report = {
        'timestamp': timestamp,
        'system_resources': check_system_resources(),
        'application': check_application_health(),
        'database': check_database(),
        'services': check_services()
    }
    
    # Determinar estado general
    overall_status = 'OK'
    issues = []
    
    if report['system_resources']:
        for resource, data in report['system_resources'].items():
            if data['status'] != 'OK':
                overall_status = 'WARNING'
                issues.append(f"{resource.upper()} alto: {data['percent']}%")
    
    if report['application']['status'] != 'OK':
        overall_status = 'ERROR'
        issues.append("Aplicación no responde correctamente")
    
    if report['database']['status'] != 'OK':
        overall_status = 'ERROR'
        issues.append("Error en base de datos")
    
    for service, data in report['services'].items():
        if data['status'] != 'OK':
            overall_status = 'ERROR'
            issues.append(f"Servicio {service} inactivo")
    
    report['overall_status'] = overall_status
    report['issues'] = issues
    
    return report

def send_alert(report):
    """Enviar alerta si hay problemas"""
    if report['overall_status'] in ['WARNING', 'ERROR']:
        alert_message = f"""
🚨 ALERTA - Los Lirios SA
Estado: {report['overall_status']}
Timestamp: {report['timestamp']}

Problemas detectados:
{chr(10).join(['- ' + issue for issue in report['issues']])}

Detalles completos en: {LOG_FILE}
        """
        
        logging.warning(f"ALERTA: {alert_message}")
        
        # Aquí podrías enviar email, Slack, Discord, etc.
        # send_email_alert(alert_message)
        # send_slack_alert(alert_message)

def main():
    """Función principal"""
    try:
        report = generate_report()
        
        # Log del reporte
        logging.info(f"Health Check - Estado: {report['overall_status']}")
        
        # Mostrar en consola si se ejecuta manualmente
        if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
            print(json.dumps(report, indent=2))
        
        # Enviar alertas si hay problemas
        send_alert(report)
        
        # Exit code basado en el estado
        if report['overall_status'] == 'ERROR':
            sys.exit(1)
        elif report['overall_status'] == 'WARNING':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        logging.error(f"Error en health check: {e}")
        sys.exit(3)

if __name__ == '__main__':
    main()