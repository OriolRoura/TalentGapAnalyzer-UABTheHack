"""
Enhanced LLM Response Cache
============================

Sistema de caché mejorado para respuestas de LLM con:
- Almacenamiento persistente en disco
- TTL configurable por tipo de consulta
- Estadísticas y monitoreo de uso
- Limpieza automática de entradas expiradas
- Compresión para ahorrar espacio
"""

import os
import json
import time
import hashlib
import gzip
from typing import Dict, Optional, Any, Literal
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
import pickle


@dataclass
class CacheEntry:
    """Entrada del caché con metadata."""
    key: str
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    created_at: float
    expires_at: float
    access_count: int
    last_accessed: float
    request_hash: str
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return time.time() > self.expires_at
    
    def is_valid(self) -> bool:
        """Verifica si la entrada es válida (no expirada)."""
        return not self.is_expired()
    
    def mark_accessed(self):
        """Marca la entrada como accedida."""
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class CacheStats:
    """Estadísticas del caché."""
    total_entries: int = 0
    total_hits: int = 0
    total_misses: int = 0
    total_saves: int = 0
    cache_size_bytes: int = 0
    hit_rate: float = 0.0
    cost_saved_usd: float = 0.0
    
    def update_hit_rate(self):
        """Actualiza la tasa de aciertos."""
        total = self.total_hits + self.total_misses
        self.hit_rate = (self.total_hits / total * 100) if total > 0 else 0.0


class EnhancedLLMCache:
    """
    Caché mejorado para respuestas de LLM con persistencia y estadísticas.
    """
    
    # TTL por tipo de consulta (en segundos)
    TTL_CONFIG = {
        'narrative': 3600,           # 1 hora - narrativas pueden cambiar
        'recommendations': 1800,     # 30 min - recomendaciones dinámicas
        'analysis': 7200,            # 2 horas - análisis más estables
        'summary': 3600,             # 1 hora - resúmenes ejecutivos
        'plan': 1800,                # 30 min - planes de desarrollo
        'default': 3600              # 1 hora por defecto
    }
    
    def __init__(self, 
                 cache_dir: str = ".cache/llm",
                 max_size_mb: int = 100,
                 enable_compression: bool = True,
                 auto_cleanup: bool = True):
        """
        Inicializa el caché mejorado.
        
        Args:
            cache_dir: Directorio para almacenar el caché
            max_size_mb: Tamaño máximo del caché en MB
            enable_compression: Si comprimir las entradas
            auto_cleanup: Si limpiar automáticamente entradas expiradas
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.enable_compression = enable_compression
        self.auto_cleanup = auto_cleanup
        
        # Lock para operaciones thread-safe
        self.lock = Lock()
        
        # Índice en memoria para acceso rápido
        self.index: Dict[str, CacheEntry] = {}
        
        # Estadísticas
        self.stats = CacheStats()
        
        # Cargar índice existente
        self._load_index()
        
        # Limpiar si es necesario
        if auto_cleanup:
            self._cleanup_expired()
        
        print(f"✅ Enhanced LLM Cache initialized")
        print(f"   📁 Cache dir: {self.cache_dir}")
        print(f"   📊 Entries: {len(self.index)}")
        print(f"   💾 Size: {self.stats.cache_size_bytes / 1024 / 1024:.2f} MB")
    
    def _generate_cache_key(self, 
                           prompt: str,
                           model: str,
                           system_prompt: Optional[str] = None,
                           temperature: float = 0.7,
                           request_type: str = 'default') -> tuple[str, str]:
        """
        Genera clave de caché única.
        
        Returns:
            (cache_key, request_hash)
        """
        # Combinar todos los parámetros relevantes
        key_parts = [
            prompt,
            model,
            system_prompt or "",
            str(temperature),
            request_type
        ]
        
        combined = "|".join(key_parts)
        request_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        # Clave legible + hash
        cache_key = f"{request_type}_{model}_{request_hash[:16]}"
        
        return cache_key, request_hash
    
    def get(self,
           prompt: str,
           model: str,
           system_prompt: Optional[str] = None,
           temperature: float = 0.7,
           request_type: str = 'default') -> Optional[Dict[str, Any]]:
        """
        Obtiene respuesta del caché si existe.
        
        Returns:
            Dict con la respuesta o None si no existe/expiró
        """
        with self.lock:
            cache_key, request_hash = self._generate_cache_key(
                prompt, model, system_prompt, temperature, request_type
            )
            
            # Buscar en índice
            if cache_key not in self.index:
                self.stats.total_misses += 1
                self.stats.update_hit_rate()
                return None
            
            entry = self.index[cache_key]
            
            # Verificar si expiró
            if entry.is_expired():
                # Eliminar entrada expirada
                self._remove_entry(cache_key)
                self.stats.total_misses += 1
                self.stats.update_hit_rate()
                return None
            
            # Hit! Cargar contenido
            try:
                content = self._load_entry_content(cache_key)
                entry.mark_accessed()
                
                # Actualizar estadísticas
                self.stats.total_hits += 1
                self.stats.cost_saved_usd += entry.cost_usd
                self.stats.update_hit_rate()
                
                # Guardar índice actualizado (async podría ser mejor)
                self._save_index()
                
                return {
                    'content': content,
                    'model': entry.model,
                    'provider': entry.provider,
                    'input_tokens': entry.input_tokens,
                    'output_tokens': entry.output_tokens,
                    'cost_usd': entry.cost_usd,
                    'cached': True,
                    'cache_age_seconds': time.time() - entry.created_at,
                    'access_count': entry.access_count
                }
            except Exception as e:
                print(f"⚠️ Error loading cache entry {cache_key}: {e}")
                # Eliminar entrada corrupta
                self._remove_entry(cache_key)
                self.stats.total_misses += 1
                self.stats.update_hit_rate()
                return None
    
    def set(self,
           prompt: str,
           model: str,
           response_content: str,
           provider: str,
           input_tokens: int,
           output_tokens: int,
           cost_usd: float,
           system_prompt: Optional[str] = None,
           temperature: float = 0.7,
           request_type: str = 'default') -> bool:
        """
        Guarda respuesta en el caché.
        
        Returns:
            True si se guardó exitosamente
        """
        with self.lock:
            cache_key, request_hash = self._generate_cache_key(
                prompt, model, system_prompt, temperature, request_type
            )
            
            # Calcular TTL según tipo de consulta
            ttl = self.TTL_CONFIG.get(request_type, self.TTL_CONFIG['default'])
            
            now = time.time()
            entry = CacheEntry(
                key=cache_key,
                content=response_content,
                model=model,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
                created_at=now,
                expires_at=now + ttl,
                access_count=0,
                last_accessed=now,
                request_hash=request_hash
            )
            
            try:
                # Guardar contenido a disco
                self._save_entry_content(cache_key, response_content)
                
                # Actualizar índice
                self.index[cache_key] = entry
                
                # Actualizar stats
                self.stats.total_entries = len(self.index)
                self.stats.total_saves += 1
                self._update_cache_size()
                
                # Guardar índice
                self._save_index()
                
                # Verificar si excedemos tamaño máximo
                if self.stats.cache_size_bytes > self.max_size_bytes:
                    self._evict_lru()
                
                return True
            
            except Exception as e:
                print(f"⚠️ Error saving cache entry {cache_key}: {e}")
                return False
    
    def _save_entry_content(self, cache_key: str, content: str):
        """Guarda el contenido de una entrada."""
        file_path = self.cache_dir / f"{cache_key}.cache"
        
        # Ensure parent directory exists (in case cache_key contains path separators)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.enable_compression:
            # Comprimir con gzip
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _load_entry_content(self, cache_key: str) -> str:
        """Carga el contenido de una entrada."""
        file_path = self.cache_dir / f"{cache_key}.cache"
        
        if self.enable_compression:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                return f.read()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _remove_entry(self, cache_key: str):
        """Elimina una entrada del caché."""
        # Eliminar del índice
        if cache_key in self.index:
            del self.index[cache_key]
        
        # Eliminar archivo
        file_path = self.cache_dir / f"{cache_key}.cache"
        if file_path.exists():
            file_path.unlink()
    
    def _save_index(self):
        """Guarda el índice en disco."""
        index_path = self.cache_dir / "index.pkl"
        with open(index_path, 'wb') as f:
            pickle.dump({
                'index': self.index,
                'stats': self.stats
            }, f)
    
    def _load_index(self):
        """Carga el índice desde disco."""
        index_path = self.cache_dir / "index.pkl"
        if index_path.exists():
            try:
                with open(index_path, 'rb') as f:
                    data = pickle.load(f)
                    self.index = data.get('index', {})
                    self.stats = data.get('stats', CacheStats())
                    
                # Actualizar tamaño del caché
                self._update_cache_size()
            except Exception as e:
                print(f"⚠️ Error loading cache index: {e}")
                self.index = {}
                self.stats = CacheStats()
    
    def _update_cache_size(self):
        """Actualiza el tamaño total del caché."""
        total_size = 0
        for cache_key in self.index.keys():
            file_path = self.cache_dir / f"{cache_key}.cache"
            if file_path.exists():
                total_size += file_path.stat().st_size
        
        self.stats.cache_size_bytes = total_size
        self.stats.total_entries = len(self.index)
    
    def _cleanup_expired(self):
        """Limpia entradas expiradas."""
        expired_keys = [
            key for key, entry in self.index.items()
            if entry.is_expired()
        ]
        
        if expired_keys:
            print(f"🧹 Cleaning up {len(expired_keys)} expired cache entries")
            for key in expired_keys:
                self._remove_entry(key)
            
            self._save_index()
    
    def _evict_lru(self):
        """Elimina las entradas menos usadas recientemente."""
        if not self.index:
            return
        
        # Ordenar por último acceso
        sorted_entries = sorted(
            self.index.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Eliminar el 20% más antiguo
        num_to_evict = max(1, len(sorted_entries) // 5)
        print(f"🧹 Evicting {num_to_evict} LRU cache entries")
        
        for key, _ in sorted_entries[:num_to_evict]:
            self._remove_entry(key)
        
        self._save_index()
    
    def clear(self):
        """Limpia todo el caché."""
        with self.lock:
            # Eliminar todos los archivos
            for cache_key in list(self.index.keys()):
                self._remove_entry(cache_key)
            
            # Reset stats
            self.stats = CacheStats()
            
            # Guardar
            self._save_index()
            
            print("🗑️ Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        return {
            'total_entries': self.stats.total_entries,
            'total_hits': self.stats.total_hits,
            'total_misses': self.stats.total_misses,
            'total_saves': self.stats.total_saves,
            'hit_rate_percent': round(self.stats.hit_rate, 2),
            'cache_size_mb': round(self.stats.cache_size_bytes / 1024 / 1024, 2),
            'max_size_mb': round(self.max_size_bytes / 1024 / 1024, 2),
            'cost_saved_usd': round(self.stats.cost_saved_usd, 4),
            'compression_enabled': self.enable_compression
        }
    
    def invalidate_pattern(self, pattern: str):
        """
        Invalida todas las entradas que coincidan con un patrón.
        
        Args:
            pattern: Patrón para buscar en las claves (ej: 'narrative_', 'employee_1001')
        """
        with self.lock:
            matching_keys = [
                key for key in self.index.keys()
                if pattern in key
            ]
            
            if matching_keys:
                print(f"🗑️ Invalidating {len(matching_keys)} cache entries matching '{pattern}'")
                for key in matching_keys:
                    self._remove_entry(key)
                
                self._save_index()


# Singleton global
_cache_instance: Optional[EnhancedLLMCache] = None


def get_llm_cache() -> EnhancedLLMCache:
    """Obtiene la instancia global del caché."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = EnhancedLLMCache()
    return _cache_instance
