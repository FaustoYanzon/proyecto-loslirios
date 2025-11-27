#!/usr/bin/env python
"""
Script para ejecutar tests con diferentes configuraciones
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import time

def setup_test_environment():
    """Configurar entorno de testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'los_lirios_sa.settings')
    django.setup()

def run_all_tests(verbosity=2):
    """Ejecutar todos los tests"""
    print("🧪 Ejecutando todos los tests...")
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity, interactive=False)
    
    start_time = time.time()
    failures = test_runner.run_tests(['contabilidad_loslirios.tests'])
    end_time = time.time()
    
    duration = end_time - start_time
    
    if failures:
        print(f"❌ Tests fallidos: {failures}")
        print(f"⏱️  Tiempo total: {duration:.2f}s")
        return False
    else:
        print(f"✅ Todos los tests pasaron!")
        print(f"⏱️  Tiempo total: {duration:.2f}s")
        return True

def run_specific_tests(test_pattern, verbosity=2):
    """Ejecutar tests específicos"""
    print(f"🧪 Ejecutando tests: {test_pattern}")
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity, interactive=False)
    
    failures = test_runner.run_tests([test_pattern])
    
    if failures:
        print(f"❌ Tests fallidos: {failures}")
        return False
    else:
        print(f"✅ Tests {test_pattern} pasaron!")
        return True

def run_performance_tests():
    """Ejecutar solo tests de performance"""
    return run_specific_tests('contabilidad_loslirios.tests.test_apis.CacheAPITestCase')

def run_unit_tests():
    """Ejecutar solo tests unitarios"""
    return run_specific_tests('contabilidad_loslirios.tests.test_models')

def run_integration_tests():
    """Ejecutar solo tests de integración"""
    return run_specific_tests('contabilidad_loslirios.tests.test_views')

def run_api_tests():
    """Ejecutar solo tests de API"""
    return run_specific_tests('contabilidad_loslirios.tests.test_apis')

def main():
    """Función principal"""
    setup_test_environment()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'all':
            success = run_all_tests()
        elif command == 'unit':
            success = run_unit_tests()
        elif command == 'integration':
            success = run_integration_tests()
        elif command == 'api':
            success = run_api_tests()
        elif command == 'performance':
            success = run_performance_tests()
        elif command == 'fast':
            # Tests rápidos (sin performance)
            success = (
                run_unit_tests() and 
                run_specific_tests('contabilidad_loslirios.tests.test_forms')
            )
        else:
            print(f"❌ Comando desconocido: {command}")
            print("Comandos disponibles: all, unit, integration, api, performance, fast")
            sys.exit(1)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()