import hashlib
import json
import time
import os
from typing import Dict, Any, Optional, List
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SmartCacheManager:
    """Intelligent caching system for code analysis results"""

    def __init__(self):
        self.cache_enabled = os.getenv(
            "ENABLE_CACHE", "true").lower() == "true"
        self.cache_ttl = int(
            os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default
        self.max_cache_size = int(os.getenv("MAX_CACHE_SIZE", "1000"))

        # In-memory cache (for production, you'd use Redis)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._hit_count = 0
        self._miss_count = 0

        print(
            f"📦 Cache Manager initialized: enabled={self.cache_enabled}, ttl={self.cache_ttl}s, max_size={self.max_cache_size}")

    def _generate_cache_key(self, code: str, filename: str, analysis_type: str) -> str:
        """Generate a unique cache key for code analysis"""
        # Create a hash based on code content, filename, and analysis type
        content = f"{code}|{filename}|{analysis_type}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        if not self.cache_enabled:
            return False

        current_time = time.time()
        entry_time = cache_entry.get("timestamp", 0)
        return (current_time - entry_time) < self.cache_ttl

    def _cleanup_old_entries(self):
        """Remove expired entries and enforce size limits"""
        current_time = time.time()

        # Remove expired entries
        expired_keys = []
        for key, entry in self._cache.items():
            if (current_time - entry.get("timestamp", 0)) > self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]

        # Enforce size limit (LRU eviction)
        if len(self._cache) > self.max_cache_size:
            # Sort by access time and remove oldest
            sorted_keys = sorted(
                self._access_times.items(), key=lambda x: x[1])
            keys_to_remove = [key for key, _ in sorted_keys[:len(
                self._cache) - self.max_cache_size]]

            for key in keys_to_remove:
                if key in self._cache:
                    del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]

        if expired_keys or len(self._cache) > self.max_cache_size:
            logger.info(
                f"Cache cleanup: removed {len(expired_keys)} expired, cache size now {len(self._cache)}")

    def get(self, code: str, filename: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result"""
        if not self.cache_enabled:
            return None

        cache_key = self._generate_cache_key(code, filename, analysis_type)

        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]

            if self._is_cache_valid(cache_entry):
                # Update access time
                self._access_times[cache_key] = time.time()
                self._hit_count += 1

                logger.debug(f"Cache HIT for {filename}:{analysis_type}")
                return cache_entry.get("result")
            else:
                # Remove expired entry
                del self._cache[cache_key]
                if cache_key in self._access_times:
                    del self._access_times[cache_key]

        self._miss_count += 1
        logger.debug(f"Cache MISS for {filename}:{analysis_type}")
        return None

    def set(self, code: str, filename: str, analysis_type: str, result: Dict[str, Any]):
        """Cache analysis result"""
        if not self.cache_enabled:
            return

        cache_key = self._generate_cache_key(code, filename, analysis_type)

        # Cleanup before adding new entry
        self._cleanup_old_entries()

        cache_entry = {
            "result": result,
            "timestamp": time.time(),
            "filename": filename,
            "analysis_type": analysis_type,
            "code_size": len(code)
        }

        self._cache[cache_key] = cache_entry
        self._access_times[cache_key] = time.time()

        logger.debug(f"Cache SET for {filename}:{analysis_type}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests *
                    100) if total_requests > 0 else 0

        return {
            "enabled": self.cache_enabled,
            "total_requests": total_requests,
            "cache_hits": self._hit_count,
            "cache_misses": self._miss_count,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": len(self._cache),
            "max_cache_size": self.max_cache_size,
            "ttl_seconds": self.cache_ttl,
            "memory_usage_mb": self._estimate_memory_usage()
        }

    def _estimate_memory_usage(self) -> float:
        """Estimate cache memory usage in MB"""
        try:
            # Rough estimation based on cache content
            total_size = 0
            for entry in self._cache.values():
                # Estimate JSON size
                total_size += len(json.dumps(entry, default=str))

            return round(total_size / (1024 * 1024), 2)  # Convert to MB
        except:
            return 0.0

    def clear_cache(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._access_times.clear()
        self._hit_count = 0
        self._miss_count = 0
        logger.info("Cache cleared")

    def get_cache_entries_by_type(self) -> Dict[str, int]:
        """Get count of cache entries by analysis type"""
        type_counts = {}
        for entry in self._cache.values():
            analysis_type = entry.get("analysis_type", "unknown")
            type_counts[analysis_type] = type_counts.get(analysis_type, 0) + 1
        return type_counts


# Global cache manager instance
cache_manager = SmartCacheManager()


def cached_analysis(analysis_type: str):
    """Decorator for caching analysis results"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, code: str, filename: str = "", *args, **kwargs):
            # Try to get from cache first
            cached_result = cache_manager.get(code, filename, analysis_type)
            if cached_result is not None:
                return cached_result

            # Execute analysis
            start_time = time.time()
            result = func(self, code, filename, *args, **kwargs)
            execution_time = time.time() - start_time

            # Add performance metadata
            if isinstance(result, list):
                # For insights lists, add metadata
                cache_result = {
                    "insights": result,
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "cached": False,
                    "analysis_type": analysis_type
                }
            else:
                # For other result types
                cache_result = result.copy() if isinstance(result, dict) else result
                if isinstance(cache_result, dict):
                    cache_result["execution_time_ms"] = round(
                        execution_time * 1000, 2)
                    cache_result["cached"] = False
                    cache_result["analysis_type"] = analysis_type

            # Cache the result
            cache_manager.set(code, filename, analysis_type, cache_result)

            return cache_result

        return wrapper
    return decorator
