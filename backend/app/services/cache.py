import json
import os
import redis.asyncio as redis
from typing import Dict, Any

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))


async def get_revenue_summary(property_id: str, tenant_id: str) -> Dict[str, Any]:
    # Cache key must include tenant_id: prop-001 exists in multiple tenants,
    # so a property-only key leaks revenue across clients.
    cache_key = f"revenue:{tenant_id}:{property_id}"

    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    from app.services.reservations import calculate_total_revenue
    result = await calculate_total_revenue(property_id, tenant_id)

    await redis_client.setex(cache_key, 300, json.dumps(result))
    return result