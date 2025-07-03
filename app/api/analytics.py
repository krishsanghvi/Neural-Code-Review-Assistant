from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.core.cache_manager import cache_manager
from app.core.performance_monitor import performance_monitor

router = APIRouter()


@router.get("/cache-stats")
async def get_cache_statistics() -> Dict[str, Any]:
    """Get cache performance statistics"""
    try:
        cache_stats = cache_manager.get_cache_stats()
        cache_entries_by_type = cache_manager.get_cache_entries_by_type()

        return {
            "cache_performance": cache_stats,
            "cache_distribution": cache_entries_by_type,
            "cache_efficiency": {
                "memory_per_entry_kb": round(
                    (cache_stats["memory_usage_mb"] * 1024) /
                    max(cache_stats["cache_size"], 1), 2
                ),
                "avg_savings_estimate": f"{cache_stats['hit_rate_percent']:.1f}% faster responses"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving cache stats: {str(e)}")


@router.get("/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """Get application performance metrics"""
    try:
        perf_stats = performance_monitor.get_performance_stats()
        cache_stats = cache_manager.get_cache_stats()

        return {
            "performance_metrics": perf_stats,
            "cache_impact": {
                "hit_rate_percent": cache_stats["hit_rate_percent"],
                "estimated_time_saved_ms": round(
                    perf_stats.get("response_times", {}).get("avg_ms", 0) *
                    cache_stats["cache_hits"] *
                    (cache_stats["hit_rate_percent"] / 100), 2
                )
            },
            "health_indicators": {
                "response_time_health": "good" if perf_stats.get("response_times", {}).get("avg_ms", 0) < 5000 else "needs_attention",
                "error_rate_health": "good" if perf_stats.get("error_rate_percent", 0) < 5 else "needs_attention",
                "cache_efficiency": "excellent" if cache_stats["hit_rate_percent"] > 80 else "good" if cache_stats["hit_rate_percent"] > 50 else "needs_improvement"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving performance metrics: {str(e)}")


@router.get("/analytics")
async def get_comprehensive_analytics() -> Dict[str, Any]:
    """Get comprehensive analytics dashboard data"""
    try:
        cache_stats = cache_manager.get_cache_stats()
        perf_stats = performance_monitor.get_performance_stats()

        # Calculate some interesting derived metrics
        total_analysis_time_saved = (
            perf_stats.get("response_times", {}).get("avg_ms", 0) *
            cache_stats["cache_hits"] / 1000  # Convert to seconds
        )

        return {
            "summary": {
                "total_requests_processed": perf_stats["total_requests"],
                "average_response_time_ms": perf_stats.get("response_times", {}).get("avg_ms", 0),
                "cache_hit_rate_percent": cache_stats["hit_rate_percent"],
                "uptime_hours": perf_stats["uptime_hours"],
                "error_rate_percent": perf_stats["error_rate_percent"]
            },
            "performance_highlights": {
                "fastest_response_ms": perf_stats.get("response_times", {}).get("min_ms", 0),
                "p95_response_time_ms": perf_stats.get("response_times", {}).get("p95_ms", 0),
                "requests_per_hour": perf_stats.get("requests_per_hour", 0),
                "total_time_saved_seconds": round(total_analysis_time_saved, 1)
            },
            "cache_effectiveness": {
                "cache_size": cache_stats["cache_size"],
                "memory_usage_mb": cache_stats["memory_usage_mb"],
                "hit_rate_trend": "improving" if cache_stats["hit_rate_percent"] > 70 else "stable",
                "cache_distribution": cache_manager.get_cache_entries_by_type()
            },
            "analysis_breakdown": perf_stats.get("analysis_breakdown", {}),
            "system_health": {
                "overall_status": "healthy" if perf_stats["error_rate_percent"] < 5 and
                perf_stats.get("response_times", {}).get("avg_ms", 0) < 10000
                else "degraded",
                "cache_status": "optimal" if cache_stats["hit_rate_percent"] > 80 else "good",
                "performance_status": "excellent" if perf_stats.get("response_times", {}).get("avg_ms", 0) < 3000 else "good"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving analytics: {str(e)}")


@router.post("/cache/clear")
async def clear_cache() -> Dict[str, str]:
    """Clear the analysis cache (admin function)"""
    try:
        cache_manager.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error clearing cache: {str(e)}")
