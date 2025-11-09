"""
API Tracer - Enhanced Logging and Tracing for API Calls
========================================================

Provides comprehensive logging, tracing, and debugging capabilities for:
- AI service calls (OpenAI, Anthropic, Google)
- External API requests
- Error tracking and debugging
- Performance monitoring
"""

import os
import json
import time
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from contextvars import ContextVar

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


class LogLevel(Enum):
    """Log levels for tracing"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class APIProvider(Enum):
    """API providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    INTERNAL = "internal"


@dataclass
class APICallTrace:
    """Trace information for an API call"""
    request_id: str
    timestamp: str
    provider: str
    endpoint: str
    method: str = "POST"
    
    # Request details
    model: Optional[str] = None
    prompt_length: int = 0
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
    # Response details
    status: str = "pending"  # pending, success, error, timeout
    response_length: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    
    # Performance
    duration_ms: float = 0.0
    retry_count: int = 0
    
    # Error details
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    finish_reason: Optional[str] = None
    
    # Additional context
    user_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.user_context is None:
            self.user_context = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)


class APITracer:
    """
    Centralized API tracing and logging service.
    
    Features:
    - Structured logging with context
    - Request/response tracing
    - Error tracking with stack traces
    - Performance monitoring
    - Log file management
    """
    
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: LogLevel = LogLevel.INFO,
        enable_file_logging: bool = True,
        enable_console_logging: bool = True,
        max_log_files: int = 10
    ):
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging
        self.max_log_files = max_log_files
        
        # Create logs directory
        if self.enable_file_logging:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self._cleanup_old_logs()
        
        # Setup Python logging
        self.logger = self._setup_logger()
        
        # In-memory trace storage (for recent traces)
        self.recent_traces: List[APICallTrace] = []
        self.max_recent_traces = 100
        
        # Statistics
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_tokens': 0,
            'total_cost_usd': 0.0,
            'by_provider': {},
            'by_endpoint': {},
            'errors': []
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup Python logger with handlers"""
        logger = logging.getLogger('APITracer')
        logger.setLevel(getattr(logging, self.log_level.value))
        logger.handlers.clear()
        
        # Console handler
        if self.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if self.enable_file_logging:
            log_file = self.log_dir / f"api_trace_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _cleanup_old_logs(self):
        """Remove old log files if exceeding max_log_files"""
        if not self.log_dir.exists():
            return
        
        log_files = sorted(
            self.log_dir.glob("api_trace_*.log"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        # Remove old files
        for old_file in log_files[self.max_log_files:]:
            try:
                old_file.unlink()
                self.logger.debug(f"Deleted old log file: {old_file.name}")
            except Exception as e:
                self.logger.warning(f"Failed to delete old log: {e}")
    
    def start_trace(
        self,
        provider: str,
        endpoint: str,
        model: Optional[str] = None,
        **kwargs
    ) -> APICallTrace:
        """
        Start tracing an API call.
        
        Args:
            provider: API provider name
            endpoint: API endpoint
            model: Model name (for AI providers)
            **kwargs: Additional context
        
        Returns:
            APICallTrace object
        """
        request_id = self._generate_request_id()
        request_id_var.set(request_id)
        
        trace = APICallTrace(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            provider=provider,
            endpoint=endpoint,
            model=model,
            user_context=kwargs
        )
        
        self.logger.debug(f"🔵 START {provider}/{endpoint} [{request_id}]")
        return trace
    
    def end_trace(
        self,
        trace: APICallTrace,
        status: str = "success",
        **kwargs
    ):
        """
        End an API call trace and log results.
        
        Args:
            trace: APICallTrace object from start_trace
            status: success, error, timeout
            **kwargs: Additional results (response_length, tokens, cost, etc.)
        """
        # Update trace with results
        trace.status = status
        for key, value in kwargs.items():
            if hasattr(trace, key):
                setattr(trace, key, value)
        
        # Add to recent traces
        self.recent_traces.append(trace)
        if len(self.recent_traces) > self.max_recent_traces:
            self.recent_traces.pop(0)
        
        # Update statistics
        self._update_stats(trace)
        
        # Log based on status
        if status == "success":
            self.logger.info(
                f"✅ SUCCESS {trace.provider}/{trace.endpoint} "
                f"[{trace.request_id}] {trace.duration_ms:.0f}ms | "
                f"tokens: {trace.input_tokens + trace.output_tokens} | "
                f"cost: ${trace.cost_usd:.4f}"
            )
        elif status == "error":
            self.logger.error(
                f"❌ ERROR {trace.provider}/{trace.endpoint} "
                f"[{trace.request_id}] {trace.error_type}: {trace.error_message}"
            )
            # Save detailed error trace
            if self.enable_file_logging:
                self._save_error_trace(trace)
        
        # Log to JSON file for detailed analysis
        if self.enable_file_logging:
            self._save_trace_json(trace)
    
    def log_error(
        self,
        provider: str,
        endpoint: str,
        error: Exception,
        context: Optional[Dict] = None
    ):
        """
        Log an error with full context.
        
        Args:
            provider: API provider
            endpoint: Endpoint that failed
            error: Exception object
            context: Additional context
        """
        trace = self.start_trace(provider, endpoint, **(context or {}))
        
        trace.status = "error"
        trace.error_type = type(error).__name__
        trace.error_message = str(error)
        
        # Get stack trace
        stack_trace = traceback.format_exc()
        
        self.logger.error(
            f"❌ {provider}/{endpoint} failed: {trace.error_type}: {trace.error_message}"
        )
        self.logger.debug(f"Stack trace:\n{stack_trace}")
        
        self.end_trace(trace, status="error")
        
        # Add to error list
        self.stats['errors'].append({
            'timestamp': trace.timestamp,
            'provider': provider,
            'endpoint': endpoint,
            'error': trace.error_type,
            'message': trace.error_message
        })
        
        # Keep only last 50 errors
        if len(self.stats['errors']) > 50:
            self.stats['errors'] = self.stats['errors'][-50:]
    
    def log_ai_call(
        self,
        provider: str,
        model: str,
        prompt: str,
        response: Optional[str] = None,
        error: Optional[Exception] = None,
        **metadata
    ):
        """
        Specialized logging for AI service calls.
        
        Args:
            provider: AI provider (openai, anthropic, google)
            model: Model name
            prompt: Input prompt
            response: Model response (if successful)
            error: Exception (if failed)
            **metadata: Additional metadata (tokens, cost, etc.)
        """
        trace = self.start_trace(
            provider=provider,
            endpoint="generate",
            model=model,
            prompt_length=len(prompt)
        )
        
        start_time = time.time()
        
        if error:
            trace.status = "error"
            trace.error_type = type(error).__name__
            trace.error_message = str(error)
            
            # Parse finish reason if available
            if hasattr(error, 'finish_reason'):
                trace.finish_reason = str(error.finish_reason)
            
            self.logger.error(
                f"❌ AI Call Failed: {provider}/{model}\n"
                f"   Error: {trace.error_type}: {trace.error_message}\n"
                f"   Prompt length: {len(prompt)} chars\n"
                f"   Finish reason: {trace.finish_reason}"
            )
        else:
            trace.status = "success"
            trace.response_length = len(response) if response else 0
            
            self.logger.info(
                f"✅ AI Call Success: {provider}/{model}\n"
                f"   Prompt: {len(prompt)} chars\n"
                f"   Response: {trace.response_length} chars\n"
                f"   Tokens: {metadata.get('input_tokens', 0)} + {metadata.get('output_tokens', 0)}\n"
                f"   Cost: ${metadata.get('cost_usd', 0):.4f}"
            )
        
        trace.duration_ms = (time.time() - start_time) * 1000
        
        # Update with metadata
        for key, value in metadata.items():
            if hasattr(trace, key):
                setattr(trace, key, value)
        
        self.end_trace(trace, status=trace.status)
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"REQ-{timestamp}"
    
    def _update_stats(self, trace: APICallTrace):
        """Update internal statistics"""
        self.stats['total_calls'] += 1
        
        if trace.status == "success":
            self.stats['successful_calls'] += 1
        else:
            self.stats['failed_calls'] += 1
        
        self.stats['total_tokens'] += trace.input_tokens + trace.output_tokens
        self.stats['total_cost_usd'] += trace.cost_usd
        
        # By provider
        if trace.provider not in self.stats['by_provider']:
            self.stats['by_provider'][trace.provider] = {
                'calls': 0, 'success': 0, 'failed': 0, 'cost': 0.0
            }
        
        provider_stats = self.stats['by_provider'][trace.provider]
        provider_stats['calls'] += 1
        if trace.status == "success":
            provider_stats['success'] += 1
        else:
            provider_stats['failed'] += 1
        provider_stats['cost'] += trace.cost_usd
        
        # By endpoint
        endpoint_key = f"{trace.provider}/{trace.endpoint}"
        if endpoint_key not in self.stats['by_endpoint']:
            self.stats['by_endpoint'][endpoint_key] = {'calls': 0, 'avg_duration_ms': 0.0}
        
        endpoint_stats = self.stats['by_endpoint'][endpoint_key]
        # Running average for duration
        n = endpoint_stats['calls']
        endpoint_stats['avg_duration_ms'] = (
            (endpoint_stats['avg_duration_ms'] * n + trace.duration_ms) / (n + 1)
        )
        endpoint_stats['calls'] += 1
    
    def _save_trace_json(self, trace: APICallTrace):
        """Save trace to JSON file"""
        try:
            json_file = self.log_dir / f"traces_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(json_file, 'a', encoding='utf-8') as f:
                f.write(trace.to_json() + '\n')
        except Exception as e:
            self.logger.warning(f"Failed to save trace JSON: {e}")
    
    def _save_error_trace(self, trace: APICallTrace):
        """Save detailed error trace"""
        try:
            error_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(error_file, 'a', encoding='utf-8') as f:
                error_data = {
                    **trace.to_dict(),
                    'stack_trace': traceback.format_exc()
                }
                f.write(json.dumps(error_data, indent=2, default=str) + '\n')
        except Exception as e:
            self.logger.warning(f"Failed to save error trace: {e}")
    
    def get_recent_traces(self, limit: int = 10) -> List[Dict]:
        """Get recent API traces"""
        return [t.to_dict() for t in self.recent_traces[-limit:]]
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['successful_calls'] / self.stats['total_calls'] * 100
                if self.stats['total_calls'] > 0 else 0
            ),
            'avg_cost_per_call': (
                self.stats['total_cost_usd'] / self.stats['total_calls']
                if self.stats['total_calls'] > 0 else 0
            )
        }
    
    def get_errors(self, limit: int = 20) -> List[Dict]:
        """Get recent errors"""
        return self.stats['errors'][-limit:]
    
    def print_summary(self):
        """Print a summary of API calls"""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("API TRACER SUMMARY")
        print("="*60)
        print(f"Total Calls:     {stats['total_calls']}")
        print(f"Success Rate:    {stats['success_rate']:.1f}%")
        print(f"Total Tokens:    {stats['total_tokens']:,}")
        print(f"Total Cost:      ${stats['total_cost_usd']:.4f}")
        print(f"Avg Cost/Call:   ${stats['avg_cost_per_call']:.4f}")
        
        print("\nBy Provider:")
        for provider, pstats in stats['by_provider'].items():
            success_rate = (pstats['success'] / pstats['calls'] * 100) if pstats['calls'] > 0 else 0
            print(f"  {provider:12} | Calls: {pstats['calls']:3} | Success: {success_rate:5.1f}% | Cost: ${pstats['cost']:.4f}")
        
        print("\nTop Endpoints (by avg duration):")
        sorted_endpoints = sorted(
            stats['by_endpoint'].items(),
            key=lambda x: x[1]['avg_duration_ms'],
            reverse=True
        )[:5]
        for endpoint, estats in sorted_endpoints:
            print(f"  {endpoint:30} | Calls: {estats['calls']:3} | Avg: {estats['avg_duration_ms']:6.0f}ms")
        
        if stats['errors']:
            print(f"\nRecent Errors ({len(stats['errors'])}):")
            for err in stats['errors'][-5:]:
                print(f"  [{err['timestamp']}] {err['provider']}/{err['endpoint']}: {err['error']}")
        
        print("="*60 + "\n")


# Global tracer instance
_global_tracer: Optional[APITracer] = None


def get_tracer() -> APITracer:
    """Get or create global tracer instance"""
    global _global_tracer
    if _global_tracer is None:
        log_dir = os.getenv('API_LOG_DIR', 'logs')
        log_level_str = os.getenv('API_LOG_LEVEL', 'INFO')
        log_level = LogLevel[log_level_str.upper()]
        
        _global_tracer = APITracer(
            log_dir=log_dir,
            log_level=log_level,
            enable_file_logging=True,
            enable_console_logging=True
        )
    
    return _global_tracer
