"""
AI Service - Multi-Provider LLM Integration
===========================================

Servicio centralizado para integración con múltiples proveedores de IA:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
- Google (Gemini Pro, Gemini Flash)

Características:
- Rate limiting y gestión de costos
- Guardrails contra sesgos
- Fallback automático entre proveedores
- Caché de respuestas
- Auditoría y logging de todas las llamadas
"""

import os
import json
import time
from typing import Dict, List, Optional, Literal, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

# Import tracer
from services.api_tracer import get_tracer

# Import enhanced cache
from services.llm_cache import get_llm_cache

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    from google import genai as genai_sdk  # New SDK for structured output
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    genai_sdk = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# Constantes de costos (USD por 1M tokens)
COST_TABLE = {
    # OpenAI models
    'gpt-4': {'input': 30.0, 'output': 60.0},
    'gpt-4-turbo': {'input': 10.0, 'output': 30.0},
    'gpt-4o': {'input': 2.50, 'output': 10.0},
    'gpt-4o-mini': {'input': 0.150, 'output': 0.600},  # Best for structured outputs
    'gpt-3.5-turbo': {'input': 0.5, 'output': 1.5},
    # Anthropic models
    'claude-3-opus': {'input': 15.0, 'output': 75.0},
    'claude-3-5-sonnet': {'input': 3.0, 'output': 15.0},
    'claude-3-sonnet': {'input': 3.0, 'output': 15.0},
    # Google models
    'gemini-pro': {'input': 0.125, 'output': 0.375},
    'gemini-2.5-pro': {'input': 1.25, 'output': 5.0},
    'gemini-2.5-flash': {'input': 0.075, 'output': 0.30},
    # PublicAI models (estimación similar a modelos open source)
    'salamandra-7b': {'input': 0.10, 'output': 0.20},
    'alia-40b': {'input': 0.50, 'output': 1.00},
}


@dataclass
class AIResponse:
    """Respuesta estructurada de la IA."""
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    reasoning_trace: Optional[str] = None
    confidence_score: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'model': self.model,
            'provider': self.provider,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'cost_usd': round(self.cost_usd, 6),
            'latency_ms': round(self.latency_ms, 2),
            'timestamp': self.timestamp.isoformat(),
            'reasoning_trace': self.reasoning_trace,
            'confidence_score': self.confidence_score
        }


@dataclass 
class UsageStats:
    """Estadísticas de uso agregadas."""
    total_requests: int = 0
    total_cost_usd: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    by_model: Dict[str, Dict] = field(default_factory=lambda: defaultdict(lambda: {
        'requests': 0, 'cost': 0.0, 'input_tokens': 0, 'output_tokens': 0
    }))
    by_provider: Dict[str, Dict] = field(default_factory=lambda: defaultdict(lambda: {
        'requests': 0, 'cost': 0.0, 'input_tokens': 0, 'output_tokens': 0
    }))
    
    def add_response(self, response: AIResponse):
        """Actualiza stats con una nueva respuesta."""
        self.total_requests += 1
        self.total_cost_usd += response.cost_usd
        self.total_input_tokens += response.input_tokens
        self.total_output_tokens += response.output_tokens
        
        # Por modelo
        model_stats = self.by_model[response.model]
        model_stats['requests'] += 1
        model_stats['cost'] += response.cost_usd
        model_stats['input_tokens'] += response.input_tokens
        model_stats['output_tokens'] += response.output_tokens
        
        # Por provider
        provider_stats = self.by_provider[response.provider]
        provider_stats['requests'] += 1
        provider_stats['cost'] += response.cost_usd
        provider_stats['input_tokens'] += response.input_tokens
        provider_stats['output_tokens'] += response.output_tokens


class RateLimiter:
    """Rate limiter simple con ventana deslizante."""
    
    def __init__(self, max_requests_per_minute: int = 60):
        self.max_requests = max_requests_per_minute
        self.requests: List[float] = []
    
    def can_proceed(self) -> bool:
        """Verifica si puede hacer otra request."""
        now = time.time()
        # Limpiar requests antiguas (> 1 minuto)
        self.requests = [ts for ts in self.requests if now - ts < 60]
        return len(self.requests) < self.max_requests
    
    def wait_if_needed(self):
        """Espera si es necesario antes de proceder."""
        while not self.can_proceed():
            time.sleep(1)
        self.requests.append(time.time())


class ResponseCache:
    """Caché simple en memoria para respuestas de IA."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, tuple[AIResponse, float]] = {}
        self.ttl = ttl_seconds
    
    def _hash_request(self, prompt: str, model: str) -> str:
        """Genera hash único para request."""
        key = f"{model}:{prompt}"
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[AIResponse]:
        """Obtiene respuesta del caché si existe y es válida."""
        key = self._hash_request(prompt, model)
        if key in self.cache:
            response, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return response
            else:
                del self.cache[key]
        return None
    
    def set(self, prompt: str, model: str, response: AIResponse):
        """Guarda respuesta en caché."""
        key = self._hash_request(prompt, model)
        self.cache[key] = (response, time.time())
    
    def clear(self):
        """Limpia todo el caché."""
        self.cache.clear()


class AIService:
    """
    Servicio principal de IA con soporte multi-provider.
    """
    
    def __init__(self,
                 max_cost_per_analysis_usd: float = 0.10,
                 rate_limit_rpm: int = 60,
                 enable_cache: bool = True,
                 default_provider: Literal['openai', 'anthropic', 'google', 'publicai'] = 'openai'):
        """
        Args:
            max_cost_per_analysis_usd: Costo máximo permitido por análisis
            rate_limit_rpm: Requests por minuto permitidas
            enable_cache: Si activar caché de respuestas
            default_provider: Provider preferido por defecto
        """
        self.max_cost_per_analysis = max_cost_per_analysis_usd
        self.default_provider = default_provider
        
        # Componentes
        self.rate_limiter = RateLimiter(rate_limit_rpm)
        # Use enhanced cache instead of simple ResponseCache
        self.cache = get_llm_cache() if enable_cache else None
        self.cache_enabled = enable_cache
        self.usage_stats = UsageStats()
        
        # Inicializar clients
        self._init_clients()
        
        # Audit log
        self.audit_log: List[Dict] = []
    
    def _init_clients(self):
        """Inicializa clientes de los providers disponibles."""
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        self.publicai_api_key = None
        
        # OpenAI (API 1.0+)
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            print("✅ OpenAI client initialized")
        
        # Anthropic
        if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
            print("✅ Anthropic client initialized")
        
        # Google
        if GOOGLE_AVAILABLE and os.getenv('GOOGLE_API_KEY'):
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.google_client = genai
            print("✅ Google Gemini client initialized")
        
        # PublicAI
        if REQUESTS_AVAILABLE and os.getenv('PUBLICAI_API_KEY'):
            self.publicai_api_key = os.getenv('PUBLICAI_API_KEY')
            print("✅ PublicAI client initialized")
    
    def _log_prompt_to_file(self, prompt: str, system_prompt: Optional[str], 
                           provider: str, model: str, temperature: float):
        """
        Logs all prompts to a debug file for troubleshooting.
        Creates/appends to logs/prompts_debug.log
        """
        try:
            log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, 'prompts_debug.log')
            
            timestamp = datetime.now().isoformat()
            separator = "=" * 80
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{separator}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"PROVIDER: {provider}\n")
                f.write(f"MODEL: {model}\n")
                f.write(f"TEMPERATURE: {temperature}\n")
                f.write(f"{separator}\n")
                
                if system_prompt:
                    f.write(f"\n--- SYSTEM PROMPT ---\n")
                    f.write(f"{system_prompt}\n")
                    f.write(f"\n--- USER PROMPT ---\n")
                
                f.write(f"{prompt}\n")
                f.write(f"{separator}\n\n")
                
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"⚠️ Failed to log prompt to file: {e}")
    
    def generate(self,
                prompt: str,
                system_prompt: Optional[str] = None,
                model: Optional[str] = None,
                temperature: float = 0.7,
                max_tokens: int = 2000,
                provider: Optional[str] = None,
                request_type: str = 'default') -> AIResponse:
        """
        Genera respuesta usando el provider especificado o el default.
        
        Args:
            prompt: Prompt principal
            system_prompt: Prompt de sistema (opcional)
            model: Modelo específico a usar
            temperature: Temperatura (0-1, mayor = más creativo)
            max_tokens: Máximo de tokens a generar
            provider: Provider específico ('openai', 'anthropic', 'google')
            request_type: Tipo de request para cache TTL ('narrative', 'analysis', etc.)
        
        Returns:
            AIResponse con la respuesta generada
        """
        # Determinar provider y modelo
        provider = provider or self.default_provider
        if not model:
            model = self._get_default_model(provider)
        
        # Log prompt to file for debugging
        self._log_prompt_to_file(prompt, system_prompt, provider, model, temperature)
        
        # Verificar caché usando enhanced cache
        if self.cache_enabled and self.cache:
            cached = self.cache.get(
                prompt=prompt,
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                request_type=request_type
            )
            if cached:
                print(f"📦 Cache hit for {request_type} request with model {model}")
                print(f"   💰 Saved ${cached['cost_usd']:.4f} | Age: {cached['cache_age_seconds']:.0f}s | Access count: {cached['access_count']}")
                # Return as AIResponse
                return AIResponse(
                    content=cached['content'],
                    model=cached['model'],
                    provider=cached['provider'],
                    input_tokens=cached['input_tokens'],
                    output_tokens=cached['output_tokens'],
                    cost_usd=0.0,  # No cost for cached responses
                    latency_ms=0.0  # Instant from cache
                )
        
        # Rate limiting - only for actual API calls
        self.rate_limiter.wait_if_needed()
        
        # Generar según provider
        start_time = time.time()
        
        try:
            if provider == 'openai' and self.openai_client:
                response = self._generate_openai(prompt, system_prompt, model, temperature, max_tokens)
            elif provider == 'anthropic' and self.anthropic_client:
                response = self._generate_anthropic(prompt, system_prompt, model, temperature, max_tokens)
            elif provider == 'google' and self.google_client:
                response = self._generate_google(prompt, system_prompt, model, temperature, max_tokens)
            elif provider == 'publicai' and self.publicai_api_key:
                response = self._generate_publicai(prompt, system_prompt, model, temperature, max_tokens)
            else:
                # Fallback al siguiente disponible
                response = self._generate_fallback(prompt, system_prompt, model, temperature, max_tokens)
        
        except Exception as e:
            print(f"❌ Error with {provider}: {e}")
            # Intentar fallback (sin especificar modelo para que use defaults del provider)
            # Skip the failed provider in fallback
            response = self._generate_fallback(prompt, system_prompt, None, temperature, max_tokens, skip_provider=provider)
        
        # Calcular latencia
        latency_ms = (time.time() - start_time) * 1000
        response.latency_ms = latency_ms
        
        # Guardar en caché usando enhanced cache
        if self.cache_enabled and self.cache:
            self.cache.set(
                prompt=prompt,
                model=model,
                response_content=response.content,
                provider=response.provider,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
                system_prompt=system_prompt,
                temperature=temperature,
                request_type=request_type
            )
        
        # Actualizar stats
        self.usage_stats.add_response(response)
        
        # Audit log
        self._log_request(prompt, response)
        
        return response
    
    def _generate_openai(self, prompt: str, system_prompt: Optional[str],
                        model: str, temperature: float, max_tokens: int) -> AIResponse:
        """Genera usando OpenAI (API 1.0+)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Use new OpenAI API (1.0+)
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        return AIResponse(
            content=content,
            model=model,
            provider='openai',
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=0  # Se calcula fuera
        )
    
    def _generate_anthropic(self, prompt: str, system_prompt: Optional[str],
                           model: str, temperature: float, max_tokens: int) -> AIResponse:
        """Genera usando Anthropic."""
        message = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = message.content[0].text
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        return AIResponse(
            content=content,
            model=model,
            provider='anthropic',
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=0
        )
    
    def _generate_google(self, prompt: str, system_prompt: Optional[str],
                        model: str, temperature: float, max_tokens: int) -> AIResponse:
        """Genera usando Google Gemini."""
        tracer = get_tracer()
        trace = tracer.start_trace(
            provider="google",
            endpoint="generate_content",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_length=len(prompt)
        )
        start_time = time.time()
        
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Configure safety settings to allow business/HR content
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            tracer.logger.debug(f"📤 Sending request to Google Gemini: {model}")
            tracer.logger.debug(f"   Prompt length: {len(full_prompt)} chars")
            tracer.logger.debug(f"   Safety settings: ALL HARM CATEGORIES BLOCKED_NONE")
            
            gemini_model = self.google_client.GenerativeModel(
                model,
                safety_settings=safety_settings
            )
            response = gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            # Check if response was blocked by safety filters
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else 'UNKNOWN'
                trace.finish_reason = str(finish_reason)
                trace.error_type = "SafetyFilterBlocked"
                trace.error_message = f"Google Gemini blocked response. Finish reason: {finish_reason}"
                trace.duration_ms = (time.time() - start_time) * 1000
                
                tracer.logger.error(
                    f"🚫 Google Gemini BLOCKED response\n"
                    f"   Model: {model}\n"
                    f"   Finish reason: {finish_reason}\n"
                    f"   Prompt length: {len(full_prompt)} chars\n"
                    f"   Temperature: {temperature}\n"
                    f"   Candidates: {len(response.candidates) if response.candidates else 0}"
                )
                
                tracer.end_trace(trace, status="error", duration_ms=trace.duration_ms)
                raise ValueError(f"Google Gemini blocked response. Finish reason: {finish_reason}. Try with different prompt or use another provider.")
        
        except Exception as e:
            trace.duration_ms = (time.time() - start_time) * 1000
            trace.error_type = type(e).__name__
            trace.error_message = str(e)
            
            tracer.logger.error(
                f"❌ Google Gemini call failed\n"
                f"   Model: {model}\n"
                f"   Error: {type(e).__name__}: {str(e)}\n"
                f"   Duration: {trace.duration_ms:.0f}ms"
            )
            
            tracer.end_trace(trace, status="error", duration_ms=trace.duration_ms)
            raise
        
        # Success path
        content = response.text
        # Gemini no expone tokens directamente, estimamos
        input_tokens = len(full_prompt.split()) * 1.3  # Estimación
        output_tokens = len(content.split()) * 1.3
        
        cost = self._calculate_cost(model, int(input_tokens), int(output_tokens))
        duration_ms = (time.time() - start_time) * 1000
        
        # Log success
        tracer.logger.info(
            f"✅ Google Gemini SUCCESS\n"
            f"   Model: {model}\n"
            f"   Response length: {len(content)} chars\n"
            f"   Estimated tokens: {int(input_tokens)} + {int(output_tokens)}\n"
            f"   Cost: ${cost:.4f}\n"
            f"   Duration: {duration_ms:.0f}ms"
        )
        
        # End trace
        tracer.end_trace(
            trace,
            status="success",
            duration_ms=duration_ms,
            response_length=len(content),
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            cost_usd=cost
        )
        
        return AIResponse(
            content=content,
            model=model,
            provider='google',
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            cost_usd=cost,
            latency_ms=duration_ms
        )
    
    def generate_structured(self, prompt: str, system_prompt: Optional[str],
                           response_schema: type, model: Optional[str] = None,
                           provider: Optional[str] = None,
                           temperature: float = 0.7) -> Dict:
        """
        Generate structured output using native JSON schema support.
        Supports OpenAI (gpt-4o, gpt-4o-mini) and Google Gemini.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            response_schema: Pydantic model class for response schema
            model: Specific model to use (optional, will use provider default)
            provider: 'openai' or 'google' (optional, will use default_provider)
            temperature: Generation temperature
            
        Returns:
            Validated Pydantic model instance converted to dict
        """
        # Determine provider
        provider = provider or self.default_provider
        
        # Route to appropriate provider
        if provider == 'openai':
            return self._generate_structured_openai(prompt, system_prompt, response_schema, model, temperature)
        elif provider == 'google':
            return self._generate_structured_google(prompt, system_prompt, response_schema, model, temperature)
        else:
            raise ValueError(f"Structured output not supported for provider: {provider}. Use 'openai' or 'google'.")
    
    def _generate_structured_openai(self, prompt: str, system_prompt: Optional[str],
                                   response_schema: type, model: Optional[str],
                                   temperature: float) -> Dict:
        """Generate structured output using OpenAI's Structured Outputs feature."""
        if not OPENAI_AVAILABLE or not self.openai_client:
            raise ValueError("OpenAI client not available. Check OPENAI_API_KEY.")
        
        # Use gpt-4o-mini by default (best cost/performance for structured outputs)
        model = model or 'gpt-4o-mini'
        
        tracer = get_tracer()
        start_time = time.time()
        
        trace = tracer.start_trace(
            provider="openai",
            endpoint="chat_completions_structured",
            model=model,
            temperature=temperature,
            prompt_length=len(prompt)
        )
        
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            tracer.logger.info(
                f"🤖 Generating STRUCTURED output from OpenAI\n"
                f"   Model: {model}\n"
                f"   Schema: {response_schema.__name__}\n"
                f"   Prompt length: {len(prompt)} chars"
            )
            
            # Generate with structured output (OpenAI Structured Outputs)
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_schema.__name__,
                        "schema": response_schema.model_json_schema(),
                        "strict": True
                    }
                }
            )
            
            # Extract content
            content = response.choices[0].message.content
            
            # Validate and parse response
            validated_response = response_schema.model_validate_json(content)
            
            # Get actual tokens and cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self._calculate_cost(model, input_tokens, output_tokens)
            duration_ms = (time.time() - start_time) * 1000
            
            tracer.logger.info(
                f"✅ STRUCTURED output generated successfully\n"
                f"   Model: {model}\n"
                f"   Response length: {len(content)} chars\n"
                f"   Tokens: {input_tokens} + {output_tokens}\n"
                f"   Cost: ${cost:.4f}\n"
                f"   Duration: {duration_ms:.0f}ms"
            )
            
            tracer.end_trace(
                trace,
                status="success",
                duration_ms=duration_ms,
                response_length=len(content),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost
            )
            
            # Track usage
            ai_response = AIResponse(
                content=content,
                model=model,
                provider='openai',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                latency_ms=duration_ms
            )
            self.usage_stats.add_response(ai_response)
            
            return validated_response.model_dump()
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            trace.duration_ms = duration_ms
            trace.error_type = type(e).__name__
            trace.error_message = str(e)
            
            tracer.logger.error(
                f"❌ OpenAI structured output generation FAILED\n"
                f"   Model: {model}\n"
                f"   Error: {type(e).__name__}: {str(e)}\n"
                f"   Duration: {duration_ms:.0f}ms"
            )
            
            tracer.end_trace(trace, status="error", duration_ms=duration_ms)
            raise
    
    def _generate_structured_google(self, prompt: str, system_prompt: Optional[str],
                                   response_schema: type, model: Optional[str],
                                   temperature: float) -> Dict:
        """Generate structured output using Google Gemini's native JSON schema support."""
        if not GOOGLE_AVAILABLE or not genai_sdk:
            raise ValueError("Google Gemini SDK not available. Install: pip install google-genai")
        
        # Use gemini-2.5-flash by default (faster and cheaper for structured outputs)
        model = model or 'gemini-2.5-flash'
        
        tracer = get_tracer()
        start_time = time.time()
        
        trace = tracer.start_trace(
            provider="google",
            endpoint="generate_content_structured",
            model=model,
            temperature=temperature,
            prompt_length=len(prompt)
        )
        
        try:
            # Initialize client with API key
            client = genai_sdk.Client(api_key=os.getenv('GOOGLE_API_KEY'))
            
            # Build full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            tracer.logger.info(
                f"🤖 Generating STRUCTURED output from Google Gemini\n"
                f"   Model: {model}\n"
                f"   Schema: {response_schema.__name__}\n"
                f"   Prompt length: {len(full_prompt)} chars"
            )
            
            # Generate with structured output
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": response_schema.model_json_schema(),
                    "temperature": temperature,
                }
            )
            
            # Validate and parse response
            validated_response = response_schema.model_validate_json(response.text)
            
            # Estimate tokens and cost
            input_tokens = len(full_prompt.split()) * 1.3
            output_tokens = len(response.text.split()) * 1.3
            cost = self._calculate_cost(model, int(input_tokens), int(output_tokens))
            duration_ms = (time.time() - start_time) * 1000
            
            tracer.logger.info(
                f"✅ STRUCTURED output generated successfully\n"
                f"   Model: {model}\n"
                f"   Response length: {len(response.text)} chars\n"
                f"   Estimated tokens: {int(input_tokens)} + {int(output_tokens)}\n"
                f"   Cost: ${cost:.4f}\n"
                f"   Duration: {duration_ms:.0f}ms"
            )
            
            tracer.end_trace(
                trace,
                status="success",
                duration_ms=duration_ms,
                response_length=len(response.text),
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                cost_usd=cost
            )
            
            # Track usage - create AIResponse for stats
            ai_response = AIResponse(
                content=response.text,
                model=model,
                provider='google',
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                cost_usd=cost,
                latency_ms=duration_ms
            )
            self.usage_stats.add_response(ai_response)
            
            return validated_response.model_dump()
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            trace.duration_ms = duration_ms
            trace.error_type = type(e).__name__
            trace.error_message = str(e)
            
            tracer.logger.error(
                f"❌ Structured output generation FAILED\n"
                f"   Model: {model}\n"
                f"   Error: {type(e).__name__}: {str(e)}\n"
                f"   Duration: {duration_ms:.0f}ms"
            )
            
            tracer.end_trace(trace, status="error", duration_ms=duration_ms)
            raise
    
    def _generate_publicai(self, prompt: str, system_prompt: Optional[str],
                          model: str, temperature: float, max_tokens: int) -> AIResponse:
        """Genera usando PublicAI (Salamandra/ALIA models)."""
        tracer = get_tracer()
        start_time = time.time()
        
        # Start trace
        trace = tracer.start_trace(
            provider="publicai",
            endpoint="chat/completions",
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.publicai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                "https://api.publicai.co/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract content and tokens
            content = result['choices'][0]['message']['content']
            input_tokens = result.get('usage', {}).get('prompt_tokens', 0)
            output_tokens = result.get('usage', {}).get('completion_tokens', 0)
            
            # Calculate cost
            cost = self._calculate_cost('alia-40b' if 'ALIA' in model else 'salamandra-7b', 
                                       input_tokens, output_tokens)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log success
            tracer.logger.info(
                f"✅ PublicAI SUCCESS\n"
                f"   Model: {model}\n"
                f"   Response length: {len(content)} chars\n"
                f"   Tokens: {input_tokens} + {output_tokens}\n"
                f"   Cost: ${cost:.4f}\n"
                f"   Duration: {duration_ms:.0f}ms"
            )
            
            # End trace
            tracer.end_trace(
                trace,
                status="success",
                duration_ms=duration_ms,
                response_length=len(content),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost
            )
            
            return AIResponse(
                content=content,
                model=model,
                provider='publicai',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                latency_ms=duration_ms
            )
            
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"PublicAI API error: {str(e)}"
            
            tracer.logger.error(
                f"❌ PublicAI ERROR\n"
                f"   Model: {model}\n"
                f"   Error: {error_msg}\n"
                f"   Duration: {duration_ms:.0f}ms"
            )
            
            tracer.end_trace(trace, status="error", duration_ms=duration_ms)
            raise Exception(error_msg)
    
    def _generate_fallback(self, prompt: str, system_prompt: Optional[str],
                          model: Optional[str], temperature: float, max_tokens: int,
                          skip_provider: Optional[str] = None) -> AIResponse:
        """Intenta con providers alternativos en orden de preferencia."""
        # OpenAI first (reliable, good structured outputs), then Google, PublicAI
        providers = ['openai', 'google', 'publicai', 'anthropic']
        
        # Skip the provider that just failed
        if skip_provider:
            providers = [p for p in providers if p != skip_provider]
            print(f"🔄 Fallback skipping failed provider: {skip_provider}")
        
        for provider in providers:
            try:
                # Use default model for each provider
                provider_model = self._get_default_model(provider) if not model else model
                
                if provider == 'openai' and self.openai_client:
                    print(f"🔄 Trying OpenAI fallback (gpt-4o-mini)...")
                    return self._generate_openai(prompt, system_prompt, 'gpt-4o-mini', temperature, max_tokens)
                elif provider == 'google' and self.google_client:
                    print(f"🔄 Trying Google fallback (gemini-2.5-flash)...")
                    return self._generate_google(prompt, system_prompt, 'gemini-2.5-flash', temperature, max_tokens)
                elif provider == 'publicai' and self.publicai_api_key:
                    print(f"🔄 Trying PublicAI fallback...")
                    return self._generate_publicai(prompt, system_prompt, 'BSC-LT/ALIA-40b-instruct_Q8_0', temperature, max_tokens)
                elif provider == 'anthropic' and self.anthropic_client:
                    print(f"🔄 Trying Anthropic fallback...")
                    return self._generate_anthropic(prompt, system_prompt, 'claude-3-5-sonnet-20241022', temperature, max_tokens)
            except Exception as e:
                print(f"⚠️ Fallback {provider} failed: {e}")
                continue
        
        raise Exception("All providers failed. Check API keys and connectivity.")
    
    def _get_default_model(self, provider: str) -> str:
        """Obtiene modelo por defecto para un provider."""
        defaults = {
            'openai': 'gpt-4o-mini',  # Best cost/performance for structured outputs
            'anthropic': 'claude-3-5-sonnet-20241022',
            'google': 'gemini-2.5-flash',  # Fast and cheap for structured
            'publicai': 'BSC-LT/ALIA-40b-instruct_Q8_0'  # ALIA-40B for complex reasoning
        }
        return defaults.get(provider, 'gpt-4o-mini')
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calcula costo de la request."""
        if model not in COST_TABLE:
            # Buscar modelo similar
            for key in COST_TABLE:
                if key in model:
                    model = key
                    break
            else:
                return 0.0  # No encontrado, retornar 0
        
        costs = COST_TABLE[model]
        input_cost = (input_tokens / 1_000_000) * costs['input']
        output_cost = (output_tokens / 1_000_000) * costs['output']
        return input_cost + output_cost
    
    def _log_request(self, prompt: str, response: AIResponse):
        """Registra request en audit log."""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'prompt_preview': prompt[:200] + '...' if len(prompt) > 200 else prompt,
            'model': response.model,
            'provider': response.provider,
            'cost_usd': response.cost_usd,
            'tokens': {
                'input': response.input_tokens,
                'output': response.output_tokens
            }
        })
    
    def get_usage_stats(self) -> Dict:
        """Retorna estadísticas de uso."""
        return {
            'total_requests': self.usage_stats.total_requests,
            'total_cost_usd': round(self.usage_stats.total_cost_usd, 4),
            'total_tokens': {
                'input': self.usage_stats.total_input_tokens,
                'output': self.usage_stats.total_output_tokens,
                'total': self.usage_stats.total_input_tokens + self.usage_stats.total_output_tokens
            },
            'by_model': dict(self.usage_stats.by_model),
            'by_provider': dict(self.usage_stats.by_provider),
            'cost_per_request_avg': round(
                self.usage_stats.total_cost_usd / max(self.usage_stats.total_requests, 1), 
                6
            )
        }
    
    def estimate_analysis_cost(self, num_employees: int) -> Dict[str, float]:
        """
        Estima costo de análisis completo.
        
        Args:
            num_employees: Número de empleados a analizar
        
        Returns:
            Estimaciones de costo por provider
        """
        # Estimaciones basadas en tokens promedio por empleado
        tokens_per_employee = {
            'input': 2000,   # Prompt + contexto
            'output': 1500   # Recomendaciones + narrativa
        }
        
        estimates = {}
        for model, costs in COST_TABLE.items():
            input_cost = (tokens_per_employee['input'] * num_employees / 1_000_000) * costs['input']
            output_cost = (tokens_per_employee['output'] * num_employees / 1_000_000) * costs['output']
            estimates[model] = round(input_cost + output_cost, 4)
        
        return estimates
    
    def check_budget(self, projected_cost: float) -> bool:
        """Verifica si el costo proyectado está dentro del budget."""
        return projected_cost <= self.max_cost_per_analysis
    
    def export_audit_log(self, filepath: str):
        """Exporta audit log a archivo JSON."""
        with open(filepath, 'w') as f:
            json.dump({
                'exported_at': datetime.now().isoformat(),
                'usage_stats': self.get_usage_stats(),
                'audit_log': self.audit_log
            }, f, indent=2)
        print(f"📄 Audit log exported to {filepath}")
