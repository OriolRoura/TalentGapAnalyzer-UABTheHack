#!/usr/bin/env python3
"""
Script de prueba para el análisis de gap con el algoritmo de Samya
Ejecutar con el servidor corriendo en http://localhost:8000
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_gap_analysis():
    """Prueba el endpoint de análisis de gap"""
    
    print("🧪 TEST: Análisis de Gap con Algoritmo de Samya")
    print("=" * 60)
    
    # 1. Verificar que el servidor está corriendo
    print("\n1️⃣ Verificando servidor...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ Servidor activo")
        else:
            print("   ❌ Servidor respondió con error")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar al servidor")
        print("   💡 Asegúrate de que el servidor esté corriendo: cd api && python main.py")
        return
    
    # 2. Obtener lista de empleados
    print("\n2️⃣ Obteniendo empleados...")
    response = requests.get(f"{BASE_URL}/employees/")
    if response.status_code == 200:
        data = response.json()
        # El endpoint devuelve {total: X, employees: [...]}
        employees = data.get('employees', [])
        print(f"   ✅ {len(employees)} empleados disponibles")
        if employees:
            first_emp = employees[0]
            print(f"   📋 Ejemplo: {first_emp['nombre']} - {first_emp['chapter']}")
    else:
        print("   ❌ Error obteniendo empleados")
        return
    
    # 3. Obtener lista de roles
    print("\n3️⃣ Obteniendo roles objetivo...")
    response = requests.get(f"{BASE_URL}/roles/")
    if response.status_code == 200:
        data = response.json()
        # El endpoint devuelve {total: X, roles: [...]}
        roles = data.get('roles', [])
        print(f"   ✅ {len(roles)} roles disponibles")
        if roles:
            first_role = roles[0]
            print(f"   📋 Ejemplo: {first_role['id']} - {first_role['titulo']}")
            target_roles = [first_role['id']]  # Tomar el primer rol como ejemplo
    else:
        print("   ❌ Error obteniendo roles")
        return
    
    # 4. Solicitar análisis de gap
    print("\n4️⃣ Solicitando análisis de gap...")
    analysis_request = {
        "analysis_name": "Test Gap Analysis - Automated",
        "description": "Análisis de gap automatizado para testing del algoritmo de Samya",
        "target_roles": target_roles,
        "timeline": "12_meses",
        "include_employees": None,  # Analizar todos
        "include_chapters": None,    # Todos los chapters
        "algorithm_weights": {
            "skills": 0.50,
            "responsibilities": 0.25,
            "ambitions": 0.15,
            "dedication": 0.10
        }
    }
    
    print(f"   📤 Request: {json.dumps(analysis_request, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/hr/analysis/request",
        json=analysis_request
    )
    
    if response.status_code == 200:
        result = response.json()
        analysis_id = result['analysis_id']
        print(f"   ✅ Análisis iniciado")
        print(f"   🆔 Analysis ID: {analysis_id}")
        print(f"   📊 Status: {result['status']}")
        print(f"   💬 Mensaje: {result['message']}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.text}")
        return
    
    # 5. Obtener resultados
    print(f"\n5️⃣ Obteniendo resultados del análisis...")
    response = requests.get(f"{BASE_URL}/hr/analysis/{analysis_id}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"   ✅ Análisis completado")
        print(f"   📊 Total resultados: {results['total_results']}")
        
        # Mostrar top 5 mejores matches
        if results['results']:
            print("\n   🏆 TOP 5 MEJORES MATCHES:")
            print("   " + "-" * 50)
            for i, match in enumerate(results['results'][:5], 1):
                print(f"\n   #{i} {match['employee_name']}")
                print(f"      Role: {match['target_role_title']}")
                print(f"      Gap Score: {match['overall_gap_score']:.2f}%")
                print(f"      Classification: {match['classification']}")
                print(f"      Responsibilities Gap: {match['responsibilities_gap']:.2f}%")
                print(f"      Ambitions Alignment: {match['ambitions_alignment']:.2f}%")
                if match['recommendations']:
                    print(f"      💡 Acción: {match['recommendations'][0]}")
        
        # Estadísticas por clasificación
        print("\n   📈 DISTRIBUCIÓN POR CLASIFICACIÓN:")
        classifications = {}
        for result in results['results']:
            cls = result['classification']
            classifications[cls] = classifications.get(cls, 0) + 1
        
        for cls, count in sorted(classifications.items()):
            print(f"      {cls}: {count} empleados")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print(f"💡 Ver resultados completos en: {BASE_URL}/hr/analysis/{analysis_id}")
        
    else:
        print(f"   ❌ Error obteniendo resultados: {response.status_code}")
        print(f"   {response.text}")


def test_single_employee_gap():
    """Prueba de análisis de gap para un solo empleado-rol"""
    
    print("\n\n🧪 TEST: Análisis Individual (Empleado vs Rol)")
    print("=" * 60)
    
    # Obtener un empleado y un rol para probar
    emp_response = requests.get(f"{BASE_URL}/employees/")
    role_response = requests.get(f"{BASE_URL}/roles/")
    
    if emp_response.status_code == 200 and role_response.status_code == 200:
        emp_data = emp_response.json()
        role_data = role_response.json()
        
        employees = emp_data.get('employees', [])
        roles = role_data.get('roles', [])
        
        if employees and roles:
            employee = employees[0]
            role = roles[0]
            
            print(f"\n👤 Empleado: {employee['nombre']}")
            print(f"🎯 Rol objetivo: {role['titulo']}")
            
            # Hacer análisis solo para este par
            analysis_request = {
                "analysis_name": f"Individual Analysis: {employee['nombre']} vs {role['titulo']}",
                "description": "Análisis individual para testing",
                "target_roles": [role['id']],
                "timeline": "12_meses",
                "include_employees": [employee['id_empleado']],
                "include_chapters": None,
                "algorithm_weights": None  # Usar pesos por defecto
            }
            
            response = requests.post(
                f"{BASE_URL}/hr/analysis/request",
                json=analysis_request
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_id = result['analysis_id']
                
                # Obtener resultado
                time.sleep(0.5)  # Pequeña espera
                results_response = requests.get(f"{BASE_URL}/hr/analysis/{analysis_id}")
                
                if results_response.status_code == 200:
                    results = results_response.json()
                    if results['results']:
                        match = results['results'][0]
                        
                        print(f"\n📊 RESULTADO DEL ANÁLISIS:")
                        print(f"   Gap Score: {match['overall_gap_score']:.2f}%")
                        print(f"   Clasificación: {match['classification']}")
                        print(f"\n   📉 Desglose:")
                        print(f"      Responsibilities Gap: {match['responsibilities_gap']:.2f}%")
                        print(f"      Ambitions Alignment: {match['ambitions_alignment']:.2f}%")
                        print(f"      Dedication Availability: {match['dedication_availability']:.2f}%")
                        
                        if match.get('recommendations'):
                            print(f"\n   💡 RECOMENDACIONES:")
                            for i, action in enumerate(match['recommendations'], 1):
                                print(f"      {i}. {action}")
                        
                        print("\n✅ Análisis individual completado")


if __name__ == "__main__":
    try:
        test_gap_analysis()
        test_single_employee_gap()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
