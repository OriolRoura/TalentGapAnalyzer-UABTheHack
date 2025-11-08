# 🧪 Guía para Testear el Análisis de Gap con el Algoritmo de Samya

## 📋 Preparación

### 1. Asegúrate de que el servidor está corriendo
```bash
cd api
python main.py
```

El servidor debe estar activo en `http://localhost:8000`

## 🎯 Método 1: Script de Prueba Automático (RECOMENDADO)

### Ejecutar el script de test:
```bash
cd api
python test_gap_analysis.py
```

El script hará:
- ✅ Verificar que el servidor funciona
- ✅ Obtener lista de empleados y roles
- ✅ Solicitar análisis de gap usando el algoritmo de Samya
- ✅ Mostrar los TOP 5 mejores matches
- ✅ Mostrar estadísticas por clasificación
- ✅ Hacer un análisis individual empleado-rol

## 🌐 Método 2: Swagger UI (Interfaz Web)

### 1. Abrir el navegador
```
http://localhost:8000/docs
```

### 2. Navegar a la sección "hr-forms"

### 3. Probar endpoint: `POST /api/v1/hr/analysis/request`

Clic en "Try it out" y usar este JSON:

```json
{
  "target_roles": ["R-STR-LEAD"],
  "include_employees": null,
  "include_chapters": null,
  "algorithm_weights": {
    "skills": 0.50,
    "responsibilities": 0.25,
    "ambitions": 0.15,
    "dedication": 0.10
  }
}
```

### 4. Copiar el `analysis_id` de la respuesta

### 5. Probar endpoint: `GET /api/v1/hr/analysis/{analysis_id}`

Pegar el `analysis_id` y ejecutar para ver los resultados.

## 🔧 Método 3: cURL (Terminal)

### Solicitar análisis:
```bash
curl -X POST "http://localhost:8000/api/v1/hr/analysis/request" \
  -H "Content-Type: application/json" \
  -d '{
    "target_roles": ["R-STR-LEAD"],
    "include_employees": null,
    "include_chapters": null,
    "algorithm_weights": {
      "skills": 0.50,
      "responsibilities": 0.25,
      "ambitions": 0.15,
      "dedication": 0.10
    }
  }'
```

### Obtener resultados (reemplaza ANALYSIS_ID):
```bash
curl -X GET "http://localhost:8000/api/v1/hr/analysis/ANALYSIS_ID"
```

## 📊 Interpretación de Resultados

### Clasificaciones (de mejor a peor):
- **READY**: Gap < 20% - Listo para el rol inmediatamente
- **READY_WITH_SUPPORT**: Gap 20-40% - Listo con soporte (3-6 meses)
- **NEAR**: Gap 40-60% - Cerca, necesita desarrollo (6-12 meses)
- **FAR**: Gap 60-80% - Lejos, desarrollo significativo (12-18 meses)
- **NOT_VIABLE**: Gap > 80% - No viable para este rol

### Componentes del Gap:
- **skills_gap**: Brecha en habilidades técnicas (50% del score total)
- **responsibilities_gap**: Alineación de responsabilidades (25%)
- **ambitions_alignment**: Match con aspiraciones del empleado (15%)
- **dedication_availability**: Disponibilidad horaria (10%)

### Overall Gap Score:
- **Menor score = Mejor match** (0% = match perfecto, 100% = sin match)

## 🔍 Endpoints Disponibles

### Análisis de Gap:
- `POST /api/v1/hr/analysis/request` - Solicitar análisis
- `GET /api/v1/hr/analysis/{id}` - Obtener resultados

### Datos Base:
- `GET /api/v1/employees/` - Lista de empleados
- `GET /api/v1/roles/` - Lista de roles objetivo
- `GET /api/v1/roles/chapters` - Chapters disponibles
- `GET /api/v1/roles/skills` - Skills disponibles

### Estadísticas:
- `GET /api/v1/employees/stats` - Estadísticas de empleados
- `GET /api/v1/company/status` - Estado general de la empresa

## 🎨 Ejemplo de Salida

```
🏆 TOP 5 MEJORES MATCHES:

#1 Juan Pérez
   Role: Strategy Lead
   Gap Score: 15.30%
   Classification: READY
   Readiness Time: 0-3 months
   Skills Gap: 12.00%
   Responsibilities Gap: 20.00%
   💡 Acción: Employee is ready for this role!

#2 María García
   Role: Strategy Lead
   Gap Score: 35.80%
   Classification: READY_WITH_SUPPORT
   Readiness Time: 3-6 months
   Skills Gap: 45.00%
   Responsibilities Gap: 30.00%
   💡 Acción: Develop missing skills: S-ANALYTICS, S-PM
```

## 🐛 Troubleshooting

### Error: "No module named 'algorithm'"
- Asegúrate de iniciar el servidor desde la carpeta `api/`
- Verifica que existe la carpeta `algorithm/` en el directorio raíz

### Error: "Connection refused"
- El servidor no está corriendo
- Ejecuta: `cd api && python main.py`

### Resultados vacíos
- Verifica que hay empleados: `GET /api/v1/employees/`
- Verifica que hay roles: `GET /api/v1/roles/`
- Usa `include_employees` y `target_roles` para filtrar correctamente

## 📝 Notas Importantes

1. **El algoritmo corre en tiempo real** - Los resultados se calculan inmediatamente
2. **Los resultados se almacenan en memoria** - Se pierden al reiniciar el servidor
3. **Puedes personalizar los pesos** del algoritmo en el request
4. **El algoritmo de Samya** está completamente integrado y funcional

## ✅ Verificación de Integración

Para verificar que el algoritmo de Samya está funcionando:

```bash
# Ver logs del servidor al hacer una petición
# Deberías ver:
# 🔍 Running gap analysis {id}...
# ✅ Analysis complete: X gap calculations
```

¡Listo! Ahora puedes probar el análisis de gap con el algoritmo de Samya 🚀
