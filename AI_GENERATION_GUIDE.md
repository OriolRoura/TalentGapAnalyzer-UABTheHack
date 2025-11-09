# AI Generation Guide - Explainability & Auditability
## Talent Gap Analyzer - UAB TheHack 2025

---

## 📚 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Cómo Funciona la IA](#cómo-funciona-la-ia)
3. [Tipos de Reasoning](#tipos-de-reasoning)
4. [Explicabilidad y Trazabilidad](#explicabilidad-y-trazabilidad)
5. [Detección y Mitigación de Sesgos](#detección-y-mitigación-de-sesgos)
6. [Auditoría de Salidas](#auditoría-de-salidas)
7. [Mejores Prácticas](#mejores-prácticas)
8. [Troubleshooting](#troubleshooting)

---

## Visión General

El sistema de Talent Gap Analyzer integra **IA Generativa (LLMs)** para producir:

- **Narrativas automáticas** personalizadas por empleado, departamento y empresa
- **Recomendaciones inteligentes** de desarrollo profesional
- **Planes de carrera estructurados** con milestones y validación
- **Insights ejecutivos** de alto nivel para toma de decisiones

### Providers Soportados

| Provider | Modelos | Costo Estimado (100 emp) | Recomendación |
|----------|---------|------------------------|---------------|
| **Google (Gemini)** | Gemini Flash, Gemini Pro | $0.15-0.30 | ✅ **MÁS ECONÓMICO** |
| **OpenAI** | GPT-3.5-turbo, GPT-4 | $0.50-8.00 | ⚡ Balance precio/calidad |
| **Anthropic** | Claude 3.5 Sonnet, Opus | $1.50-15.00 | 🎯 Máxima calidad |

**Para producción con presupuesto limitado:** Usar **Gemini Flash** (Google)

---

## Cómo Funciona la IA

### Arquitectura del Sistema

```
┌─────────────────┐
│   Data Input    │
│ (Employee data, │
│  Gap results)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prompt Builder  │◄──── Bias-free templates
│ (Structured     │
│  prompts)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Service    │◄──── Rate limiting
│ (Multi-provider)│◄──── Cost tracking
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Bias Detector   │◄──── Pattern matching
│ (Pre + Post)    │◄──── Severity scoring
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Output Model   │
│ (Pydantic with  │
│  AI Metadata)   │
└─────────────────┘
```

### Flujo de Generación

1. **Construcción de Contexto**
   - Datos del empleado (skills, ambiciones, chapter)
   - Resultados de gap analysis
   - Roles objetivo y requisitos

2. **Validación Pre-Generación**
   - Bias detection en el prompt
   - Verificación de guardrails
   - Cost estimation

3. **Generación con LLM**
   - Prompt estructurado + System prompt con guardrails
   - Rate limiting automático
   - Fallback a otros providers si falla

4. **Validación Post-Generación**
   - Bias detection en la respuesta
   - Parsing y validación de estructura (Pydantic)
   - Marcado para human review si necesario

5. **Enriquecimiento con Metadata**
   - Modelo usado, provider, tokens, costo
   - Nivel de confianza
   - Reasoning trace (explicación del razonamiento)
   - Bias check results

---

## Tipos de Reasoning

Cada pieza de contenido generado incluye metadata indicando el tipo de razonamiento usado:

### 1. **DATA_DRIVEN** (Basado en Datos)

```json
{
  "reasoning_type": "data_driven",
  "reasoning_trace": "Based on gap analysis showing 0.35 score on OKRs skill"
}
```

- **Cuándo**: Recomendaciones basadas puramente en métricas cuantitativas
- **Confianza**: Alta (si datos son completos)
- **Explicación**: Referencias directas a scores, percentiles, gaps específicos

### 2. **RULE_BASED** (Basado en Reglas)

```json
{
  "reasoning_type": "rule_based",
  "reasoning_trace": "Applied rule: READY band triggers immediate promotion recommendation"
}
```

- **Cuándo**: Lógica de negocio predefinida (bandas, thresholds)
- **Confianza**: Media-Alta
- **Explicación**: Regla específica aplicada

### 3. **GENERATIVE** (IA Generativa)

```json
{
  "reasoning_type": "generative",
  "reasoning_trace": "LLM-generated narrative based on employee context and gap results",
  "model_used": "gpt-3.5-turbo"
}
```

- **Cuándo**: Narrativas, insights cualitativos, recomendaciones contextualizadas
- **Confianza**: Media (requiere validación)
- **Explicación**: Modelo de IA usado + inputs proporcionados

### 4. **HYBRID** (Híbrido)

```json
{
  "reasoning_type": "hybrid",
  "reasoning_trace": "Combined rule-based prioritization with AI-enhanced descriptions"
}
```

- **Cuándo**: Combinación de reglas + enriquecimiento con IA
- **Confianza**: Alta
- **Explicación**: Qué parte es regla vs. IA

---

## Explicabilidad y Trazabilidad

### Metadata de Cada Generación

Toda salida de IA incluye un objeto `AIMetadata`:

```python
{
  "model_used": "gpt-3.5-turbo",
  "provider": "openai",
  "generated_at": "2025-11-08T14:32:00Z",
  "confidence_level": "high",  # high | medium | low
  "reasoning_type": "generative",
  "reasoning_trace": "Detailed explanation of the reasoning process",
  "input_tokens": 1234,
  "output_tokens": 567,
  "cost_usd": 0.0023,
  "bias_check_passed": true,
  "human_review_required": false
}
```

### Campos Clave

- **`reasoning_trace`**: Explicación en lenguaje natural del razonamiento
- **`confidence_level`**: Nivel de confianza del sistema en la salida
  - `HIGH`: Datos completos, sin sesgos, modelo confiable
  - `MEDIUM`: Algunos datos faltantes o sesgos menores detectados
  - `LOW`: Datos insuficientes o alta incertidumbre
- **`bias_check_passed`**: Si pasó validación de sesgos
- **`human_review_required`**: Si requiere revisión humana antes de uso

### Cómo Interpretar la Confianza

```python
if metadata.confidence_level == "low" or metadata.human_review_required:
    print("⚠️ Esta salida debe ser revisada por un humano antes de usarse")
    
if not metadata.bias_check_passed:
    print("⚠️ Se detectaron posibles sesgos. Ver detalles en logs.")
```

---

## Detección y Mitigación de Sesgos

### Categorías de Sesgos Detectados

1. **Género** (`gender`)
   - Referencias explícitas a género sin justificación
   - Asociación de roles con género específico
   - Generalizaciones por género

2. **Edad** (`age`)
   - Referencias innecesarias a edad/antigüedad
   - Estereotipos generacionales
   - Juicios basados en edad

3. **Origen/Nacionalidad** (`origin`)
   - Referencias a origen étnico/nacional
   - Diferencias culturales mencionadas innecesariamente

4. **Discapacidad** (`disability`)
   - Lenguaje discriminatorio sobre capacidades
   - Términos ofensivos

5. **Estereotipos Profesionales** (`stereotype`)
   - Roles asociados a grupos demográficos
   - Generalizaciones de "lo típico"

### Niveles de Severidad

- **HIGH**: Bloquea la salida, requiere human review
- **MEDIUM**: Warning, puede usarse con precaución
- **LOW**: Informativo, mejorar el lenguaje

### Ejemplo de Detección

```python
# Input con sesgo
text = "Los ingenieros jóvenes son más innovadores"

# Resultado
{
  "has_bias": true,
  "bias_types_detected": ["age", "stereotype"],
  "high_severity_count": 1,
  "flagged_content": [
    {
      "category": "age",
      "matched_text": "ingenieros jóvenes",
      "severity": "high",
      "description": "Generalización por edad",
      "mitigation": "Basar en competencias, no edad"
    }
  ],
  "requires_human_review": true
}
```

### Guardrails Incorporados

Todos los prompts incluyen instrucciones explícitas:

```
INSTRUCCIONES CRÍTICAS - NEUTRALIDAD Y EQUIDAD:

1. LENGUAJE INCLUSIVO: Usar lenguaje neutral en género
2. NO ASUMIR GÉNERO: No hacer suposiciones
3. NO MENCIONAR EDAD: Salvo sea estrictamente relevante
4. NO MENCIONAR ORIGEN: No referenciar nacionalidad
5. BASAR EN DATOS: Solo competencias técnicas y objetivas
6. EVITAR ESTEREOTIPOS: No generalizar por demografía
7. SER OBJETIVO: Usar métricas cuantitativas
```

---

## Auditoría de Salidas

### Audit Log

El sistema mantiene un log de TODAS las llamadas a la IA:

```python
{
  "timestamp": "2025-11-08T14:32:00Z",
  "prompt_preview": "Genera recomendaciones para empleado 1001...",
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "cost_usd": 0.0023,
  "tokens": {
    "input": 1234,
    "output": 567
  }
}
```

### Exportar Audit Log

```python
# En código
ai_service.export_audit_log('audit_log_20251108.json')

# Via API
GET /api/v1/ai/stats
```

### Revisar Estadísticas de Uso

```python
GET /api/v1/ai/stats

Response:
{
  "total_requests": 150,
  "total_cost_usd": 1.23,
  "by_model": {
    "gpt-3.5-turbo": {
      "requests": 120,
      "cost": 0.98
    },
    "gemini-2.5-flash": {
      "requests": 30,
      "cost": 0.25
    }
  },
  "cost_per_request_avg": 0.0082
}
```

### Validar Calidad de Salidas

**Checklist de Validación:**

- [ ] ¿La narrativa es coherente y específica? (no genérica)
- [ ] ¿Las recomendaciones son accionables? (tienen timeline, recursos, criterios)
- [ ] ¿Pasó el bias check?
- [ ] ¿La confianza es al menos MEDIUM?
- [ ] ¿Los datos de soporte son correctos?
- [ ] ¿El reasoning trace explica claramente el razonamiento?

---

## Mejores Prácticas

### Para Usuarios del Sistema

1. **Siempre revisar metadata de confianza**
   ```python
   if narrative.ai_metadata.confidence_level == "low":
       print("⚠️ Revisar antes de usar")
   ```

2. **Validar recomendaciones contra conocimiento del negocio**
   - La IA puede no conocer políticas internas
   - Verificar que recursos mencionados existan
   - Confirmar que timelines sean realistas

3. **Reportar sesgos detectados**
   - Si encuentras contenido sesgado que pasó filtros, reportarlo
   - Ayuda a mejorar los patrones de detección

4. **Usar narrativas como punto de partida, no verdad absoluta**
   - Son análisis generados automáticamente
   - Complementar con juicio humano
   - Validar con stakeholders

### Para Desarrolladores

1. **Optimizar costos**
   ```python
   # Usar Gemini Flash para reducir costos
   AI_DEFAULT_PROVIDER=google
   
   # Habilitar caché
   AI_ENABLE_CACHE=true
   
   # Procesar en batch cuando sea posible
   POST /api/v1/ai/batch-generate
   ```

2. **Monitorear costos activamente**
   ```python
   # Estimar ANTES de generar
   estimates = ai_service.estimate_analysis_cost(num_employees=100)
   if estimates['gpt-4'] > budget:
       use_cheaper_model()
   ```

3. **Implementar rate limiting por usuario**
   - Evitar abuse del API
   - Proteger presupuesto

4. **Guardar audit logs periódicamente**
   ```python
   # Exportar diariamente
   ai_service.export_audit_log(f'logs/audit_{date}.json')
   ```

---

## Troubleshooting

### Problema: "AI service not configured"

**Causa**: No hay API keys configuradas

**Solución**:
```bash
# Configurar al menos un provider
export OPENAI_API_KEY=sk-xxx
# O
export GOOGLE_API_KEY=xxx
# O
export ANTHROPIC_API_KEY=sk-ant-xxx
```

### Problema: "High bias detected, human review required"

**Causa**: Contenido generado contiene sesgos de alta severidad

**Solución**:
1. Revisar `flagged_content` en el resultado
2. Regenerar con prompt más específico
3. Usar modo `hybrid` en lugar de puramente generativo
4. Reportar el caso para mejorar guardrails

### Problema: Costos muy altos

**Causa**: Modelo caro o demasiadas generaciones

**Solución**:
```python
# 1. Cambiar a modelo más económico
AI_DEFAULT_PROVIDER=google  # Gemini Flash

# 2. Reducir max_tokens
AI_NARRATIVE_MAX_TOKENS=1500  # En lugar de 2500

# 3. Habilitar caché agresivo
AI_CACHE_TTL_SECONDS=7200  # 2 horas

# 4. Procesar en batch con mayor cache hit rate
```

### Problema: Narrativas genéricas o poco útiles

**Causa**: Prompt no tiene suficiente contexto o temperatura muy alta

**Solución**:
```python
# 1. Reducir temperatura (más determinístico)
AI_NARRATIVE_TEMPERATURE=0.5  # En lugar de 0.7

# 2. Proporcionar más contexto en el prompt
# Incluir: ambiciones específicas, skills concretos, objetivos claros

# 3. Usar modelo más potente para casos críticos
model='gpt-4-turbo'  # En lugar de gpt-3.5
```

### Problema: Timeouts o errores de API

**Causa**: Rate limits excedidos o API caída

**Solución**:
```python
# 1. Sistema tiene fallback automático
# Intentará otros providers disponibles

# 2. Aumentar timeout
AI_REQUEST_TIMEOUT_SECONDS=60

# 3. Reducir rate limit
AI_RATE_LIMIT_RPM=30  # En lugar de 60

# 4. Procesar en batch con delays
```

---

## Interpretación de Resultados

### Ejemplo de Narrativa con Metadata

```json
{
  "id": "NAR-EMP-1001-20251108",
  "title": "Análisis de Talent Gap - Juan Pérez",
  "scope": "employee",
  "executive_summary": "Juan muestra fortalezas sólidas en análisis técnico...",
  "key_insights": [
    "Gap identificado en OKRs (score: 0.35)",
    "Alta alineación con ambiciones declaradas",
    "Ready para rol Mid con soporte en 1 skill"
  ],
  "ai_metadata": {
    "model_used": "gpt-3.5-turbo",
    "confidence_level": "high",
    "reasoning_type": "generative",
    "reasoning_trace": "Generated based on gap results showing NEAR band for target role R-STR-MID, with primary gap in S-OKR skill",
    "bias_check_passed": true,
    "human_review_required": false,
    "cost_usd": 0.0034
  }
}
```

**Cómo Interpretar:**

- ✅ **Confianza HIGH** + **Bias check passed**: Puede usarse directamente
- ✅ **Reasoning trace** explica claramente: basado en banda NEAR y gap en OKRs
- ✅ **Costo bajo**: $0.0034 por análisis individual
- ⚠️ **Siempre validar** que el skill mencionado (S-OKR) sea realmente relevante

---

## Recursos Adicionales

- **Código fuente**: `/api/services/ai_service.py`, `bias_detector.py`, `narrative_generator.py`
- **Tests**: `/api/test_ai_generation.py`
- **API Docs**: `http://localhost:8000/docs#/AI%20Insights`
- **Configuración**: `/api/.env.example`

---

## Contacto y Soporte

Para preguntas sobre el sistema de IA:
1. Revisar este documento primero
2. Consultar logs de audit (`/logs/ai_audit/`)
3. Verificar tests (`pytest test_ai_generation.py -v`)

**Principios Clave:**
- ✅ Transparencia total (audit log + metadata)
- ✅ Explicabilidad (reasoning trace en cada salida)
- ✅ Mitigación de sesgos (pre + post generación)
- ✅ Validación continua (tests automatizados)
- ✅ Optimización de costos (múltiples providers, caché)

---

*Última actualización: 8 de noviembre de 2025 - UAB TheHack 2025*
