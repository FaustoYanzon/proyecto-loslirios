#!/bin/bash
# Comandos rápidos para testing

echo "🧪 Los Lirios SA - Testing Commands"
echo "=================================="

# Tests básicos
alias test_all="python run_tests.py all"
alias test_unit="python run_tests.py unit" 
alias test_api="python run_tests.py api"
alias test_fast="python run_tests.py fast"

# Tests con Django manage.py
alias test_models="python manage.py test contabilidad_loslirios.tests.test_models --keepdb"
alias test_views="python manage.py test contabilidad_loslirios.tests.test_views --keepdb"
alias test_forms="python manage.py test contabilidad_loslirios.tests.test_forms --keepdb"

# Tests con coverage (si está instalado)
alias test_coverage="coverage run --source='.' manage.py test contabilidad_loslirios.tests && coverage report"

echo "✅ Comandos configurados!"
echo ""
echo "Uso:"
echo "  test_all       - Todos los tests"
echo "  test_unit      - Solo tests unitarios"
echo "  test_api       - Solo tests de API"
echo "  test_fast      - Tests rápidos"
echo "  test_models    - Solo tests de modelos"
echo "  test_views     - Solo tests de vistas"
echo "  test_forms     - Solo tests de formularios"
echo "  test_coverage  - Tests con reporte de cobertura"