# 🤖 Sistema de IA Generativa - Talent Gap Analyzer

## Nivel 3: IA Generativa + Narrativas Automáticas ✅

Sistema completo de IA generativa integrado en el Talent Gap Analyzer para generar insights, recomendaciones y narrativas automáticas.

---

## 🎯 Características Implementadas

### ✅ 1. Integración Multi-Provider LLM
- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Anthropic** (Claude 3.5 Sonnet, Claude 3 Opus)
- **Google** (Gemini Pro, Gemini Flash)
- Fallback automático entre providers
- Rate limiting y gestión de costos
- Caché de respuestas para optimización

### ✅ 2. Generación de Narrativas Automáticas
- **Por Empleado**: Análisis personalizado de gaps y oportunidades
- **Por Departamento**: Narrativas ejecutivas de estado del talent pipeline
- **A Nivel Empresa**: Executive summary completo con insights estratégicos
- Múltiples tonos: analytical, executive, motivational, technical

### ✅ 3. Recomendaciones Personalizadas
- Recomendaciones inteligentes por empleado
- Planes de desarrollo estructurados con milestones
- Action items específicos con timelines y recursos
- Priorización automática basada en impact y viabilidad

### ✅ 4. Detección y Mitigación de Sesgos
- 6 categorías de sesgos: género, edad, origen, discapacidad, estereotipos, lenguaje
- Validación pre y post-generación
- Guardrails incorporados en prompts
- Marcado automático para human review

### ✅ 5. Explainability y Auditabilidad
- Metadata completa en cada generación (modelo, costo, tokens, confianza)
- Reasoning trace explicando el razonamiento
- Audit log de todas las llamadas
- Exportación de logs para compliance

### ✅ 6. Optimización de Costos
- Estimación de costos ANTES de generar
- Caché para reducir requests duplicadas
- Batch processing para múltiples empleados
- **Costo target**: < $0.10 USD por análisis de empleado

---

## 📁 Estructura de Archivos

```
api/
├── services/
│   ├── ai_service.py                    # 🧠 Servicio central de IA multi-provider
│   ├── bias_detector.py                 # 🛡️ Detección de sesgos
│   ├── narrative_generator.py           # 📝 Generación de narrativas
│   └── ai_recommendation_engine.py      # 💡 Recomendaciones IA-enhanced
├── models/
│   └── ai_models.py                     # 📊 Modelos Pydantic para IA
├── routes/
│   └── ai_insights.py                   # 🌐 API endpoints de IA
├── test_ai_generation.py                # ✅ Tests de IA
├── .env.example                         # ⚙️ Configuración (con AI keys)
└── requirements.txt                     # 📦 Dependencias (openai, anthropic, etc)

AI_GENERATION_GUIDE.md                   # 📚 Guía completa de explainability
```

---

## 🚀 Quick Start

### 1. Instalar Dependencias

```bash
cd api
pip install -r requirements.txt
```

Nuevas dependencias:
```
openai>=1.0.0
anthropic>=0.7.0
google-generativeai>=0.3.0
tiktoken>=0.5.0
```

### 2. Configurar API Keys

Copiar `.env.example` a `.env` y configurar al menos un provider:

```bash
# Opción 1: Google (MÁS ECONÓMICO)
export GOOGLE_API_KEY=your-google-ai-api-key
export AI_DEFAULT_PROVIDER=google

# Opción 2: OpenAI
export OPENAI_API_KEY=sk-your-openai-key
export AI_DEFAULT_PROVIDER=openai

# Opción 3: Anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key
export AI_DEFAULT_PROVIDER=anthropic
```

**Recomendación**: Usar **Google Gemini Flash** para mejor ratio costo/calidad.

### 3. Ejecutar API

```bash
cd api
python main.py
```

La API estará disponible en `http://localhost:8000/docs`

---

## 📡 Endpoints Principales

### Recomendaciones Personalizadas
```http
GET /api/v1/ai/employee/{employee_id}/recommendations
```
Genera recomendaciones IA-enhanced para un empleado.

**Parámetros:**
- `employee_id`: ID del empleado
- `max_recommendations`: Número de recomendaciones (default: 10)
- `target_role_id`: Rol objetivo específico (opcional)

**Respuesta:**
```json
[
  {
    "id": "REC-1001-20251108-0",
    "employee_id": "1001",
    "type": "skill_development",
    "title": "Desarrollar competencia en OKRs",
    "description": "Curso estructurado de OKRs...",
    "rationale": "Gap identificado en skill estratégico crítico",
    "action_items": [
      {
        "action": "Inscribirse en curso OKRs Fundamentals",
        "timeline": "2 semanas",
        "resources_needed": ["Budget: €200", "Plataforma Coursera"],
        "success_criteria": "Certificación completada",
        "priority": "high"
      }
    ],
    "effort_level": "medium",
    "estimated_duration": "3 meses",
    "priority_score": 0.85,
    "success_probability": 0.78,
    "ai_metadata": {
      "model_used": "gpt-3.5-turbo",
      "provider": "openai",
      "confidence_level": "high",
      "reasoning_type": "generative",
      "cost_usd": 0.0034,
      "bias_check_passed": true
    }
  }
]
```

### Narrativa Individual
```http
GET /api/v1/ai/employee/{employee_id}/narrative?tone=analytical
```
Genera narrativa personalizada sobre el talent gap de un empleado.

### Plan de Desarrollo
```http
GET /api/v1/ai/employee/{employee_id}/development-plan?target_role_id=R-STR-LEAD&duration_months=6
```
Genera plan de desarrollo estructurado con milestones.

### Narrativa Departamental
```http
GET /api/v1/ai/department/{chapter}/narrative?tone=executive
```
Genera narrativa ejecutiva para un departamento.

### Resumen Ejecutivo Empresa
```http
GET /api/v1/ai/company/executive-summary
```
Genera executive summary completo de la organización.

### Estadísticas de Uso
```http
GET /api/v1/ai/stats
```
Retorna estadísticas de uso de IA (requests, costos, tokens).

### Health Check
```http
GET /api/v1/ai/health
```
Verifica estado del servicio de IA y providers disponibles.

---

## 💰 Optimización de Costos

### Estimación de Costos por Provider

Para **100 empleados** con análisis completo:

| Provider | Modelo | Costo Estimado | Tiempo Estimado |
|----------|--------|---------------|-----------------|
| **Google** | Gemini Flash | $0.15-0.30 | ~5-10 min |
| **OpenAI** | GPT-3.5-turbo | $0.50-1.00 | ~10-15 min |
| **OpenAI** | GPT-4-turbo | $3.00-8.00 | ~15-20 min |
| **Anthropic** | Claude 3.5 Sonnet | $1.50-3.00 | ~10-15 min |
| **Anthropic** | Claude 3 Opus | $8.00-15.00 | ~15-20 min |

### Estrategias de Optimización

1. **Usar Gemini Flash** (Google)
   ```bash
   AI_DEFAULT_PROVIDER=google
   ```

2. **Habilitar Caché Agresivo**
   ```bash
   AI_ENABLE_CACHE=true
   AI_CACHE_TTL_SECONDS=7200  # 2 horas
   ```

3. **Batch Processing**
   ```http
   POST /api/v1/ai/batch-generate
   {
     "employee_ids": ["1001", "1002", "1003"],
     "max_cost_usd": 0.50
   }
   ```

4. **Reducir Max Tokens**
   ```bash
   AI_NARRATIVE_MAX_TOKENS=1500  # En lugar de 2500
   ```

5. **Temperatura Más Baja** (más determinístico = menos tokens)
   ```bash
   AI_NARRATIVE_TEMPERATURE=0.5
   ```

---

## 🛡️ Detección de Sesgos

El sistema detecta y mitiga 6 categorías de sesgos:

### Categorías

1. **Género** - Referencias explícitas, asociaciones de roles
2. **Edad** - Menciones innecesarias, estereotipos generacionales
3. **Origen** - Referencias étnicas/nacionales
4. **Discapacidad** - Lenguaje discriminatorio
5. **Estereotipos** - Generalizaciones por demografía
6. **Lenguaje** - Masculino genérico, términos no inclusivos

### Niveles de Severidad

- **HIGH**: Bloquea la salida, requiere human review
- **MEDIUM**: Warning, puede usarse con precaución
- **LOW**: Informativo

### Validación Automática

```python
# Pre-generación: Valida el prompt
validation = bias_detector.validate_prompt(prompt)
if not validation['is_valid']:
    print(f"⚠️ Warnings: {validation['warnings']}")

# Post-generación: Valida la respuesta
bias_check = bias_detector.detect_bias(ai_response)
if bias_check['has_bias']:
    print(f"⚠️ Sesgos detectados: {bias_check['bias_types_detected']}")
    if bias_check['requires_human_review']:
        print("❌ Esta salida requiere revisión humana")
```

---

## 📊 Explainability

Toda generación incluye metadata completa:

```json
{
  "ai_metadata": {
    "model_used": "gpt-3.5-turbo",
    "provider": "openai",
    "generated_at": "2025-11-08T14:32:00Z",
    "confidence_level": "high",
    "reasoning_type": "generative",
    "reasoning_trace": "Generated narrative based on gap results showing NEAR band for target role with primary gap in OKRs skill",
    "input_tokens": 1234,
    "output_tokens": 567,
    "cost_usd": 0.0034,
    "bias_check_passed": true,
    "human_review_required": false
  }
}
```

### Tipos de Reasoning

- **`data_driven`**: Basado puramente en métricas cuantitativas
- **`rule_based`**: Lógica de negocio predefinida
- **`generative`**: Generado por LLM
- **`hybrid`**: Combinación de reglas + IA

Ver [AI_GENERATION_GUIDE.md](AI_GENERATION_GUIDE.md) para más detalles.

---

## ✅ Tests

Ejecutar tests de IA:

```bash
cd api
pytest test_ai_generation.py -v
```

Tests incluidos:
- ✅ Detección de sesgos (género, edad, origen, etc.)
- ✅ Validación de estructura de recomendaciones
- ✅ Calidad de narrativas (coherencia, accionabilidad)
- ✅ Cálculo de costos
- ✅ Estimación de presupuesto
- ✅ Validación de prompts

---

## 📚 Documentación Adicional

- **[AI_GENERATION_GUIDE.md](AI_GENERATION_GUIDE.md)**: Guía completa de explainability y auditabilidad
- **[api/ENDPOINTS.md](api/ENDPOINTS.md)**: Documentación de todos los endpoints
- **[api/README.md](api/README.md)**: Setup y arquitectura de la API

---

## 🎓 Criterios de Éxito (NIVEL 3) - ✅ CUMPLIDOS

| Criterio | Estado | Notas |
|----------|--------|-------|
| Narrativas coherentes y accionables | ✅ | Estructura validada con Pydantic + tests |
| Respeto restricciones organizacionales | ✅ | Basadas en datos reales de la empresa |
| Costo < $10 por 100 empleados | ✅ | Con Gemini: $0.15-0.30, GPT-3.5: $0.50-1.00 |
| Salida auditable y reproducible | ✅ | Audit log + metadata completa |
| Sin sesgos discriminatorios | ✅ | 6 categorías de detección + guardrails |
| Explainability clara | ✅ | Reasoning trace + confidence levels |

---

## 🔧 Troubleshooting

### "AI service not configured"
**Solución**: Configurar al menos un API key:
```bash
export OPENAI_API_KEY=sk-xxx
# O
export GOOGLE_API_KEY=xxx
```

### Costos muy altos
**Solución**: Usar Gemini Flash y habilitar caché:
```bash
AI_DEFAULT_PROVIDER=google
AI_ENABLE_CACHE=true
```

### Narrativas genéricas
**Solución**: Reducir temperatura y/o usar modelo más potente:
```bash
AI_NARRATIVE_TEMPERATURE=0.5
# O cambiar a GPT-4 para casos críticos
```

### Sesgos detectados
**Solución**: El sistema automáticamente marca para human review. Revisar `flagged_content` y regenerar si necesario.

---

## 📈 Próximos Pasos (Opcional)

- [ ] Fine-tuning de modelos con datos específicos de la empresa
- [ ] Integración con sistema de notificaciones (enviar recomendaciones por email)
- [ ] Dashboard interactivo para visualizar insights de IA
- [ ] A/B testing de diferentes prompts para optimizar calidad
- [ ] Integración con sistemas de LMS para aplicar recomendaciones

---

## 👥 Contribuidores

Desarrollado para **UAB TheHack 2025** - Nivel 3: IA Generativa

---

## 📝 Licencia

Este proyecto es parte del challenge UAB TheHack 2025.

---

**¿Preguntas?** Consulta [AI_GENERATION_GUIDE.md](AI_GENERATION_GUIDE.md) para documentación detallada.
