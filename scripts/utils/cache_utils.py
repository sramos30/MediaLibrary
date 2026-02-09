# base do cache
#!/usr/bin/env python3
import os
import json
import redis
from redis.exceptions import RedisError
from pathlib import Path
import xxhash

# Configs
PREFIX_SIZE = 256 * 1024 # 256KB, pode ajustar conforme necessário
HASH_FUNC = xxhash.xxh3_64  # ou xxh3_128 se preferir
TTL_SECONDS = 86400 * 1  # 1 dia

# Conexão Redis lazy com fallback
_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2,
                retry_on_timeout=True
            )
            _redis_client.ping()  # teste
        except RedisError as e:
            print(f"Redis indisponível ({e}) → fallback para memória")
            _redis_client = None
    return _redis_client

# Cache local fallback
_memory_cache = {}

def get_cached_prefix(path: Path):
    """
    Retorna (size, prefix_hash, read_size)
    Tenta Redis → memória → calcula e cacheia
    """
    size = path.stat().st_size
    cache_key = f"prefix:{path.name}:{size}"

    # Redis first
    r = get_redis()
    if r:
        try:
            cached = r.get(cache_key)
            if cached:
                return tuple(json.loads(cached))
        except RedisError:
            pass

    # Memory fallback
    if cache_key in _memory_cache:
        return _memory_cache[cache_key]

    # Compute
    read_size = min(size, PREFIX_SIZE)
    with open(path, "rb") as f:
        data = f.read(read_size)
        h = HASH_FUNC()
        h.update(data)
        prefix_hash = h.intdigest()

    result = (size, prefix_hash, read_size)

    # Cacheia
    serialized = json.dumps(result)
    if r:
        try:
            r.set(cache_key, serialized, ex=TTL_SECONDS)
        except RedisError:
            pass
    _memory_cache[cache_key] = result

    return result

def set_cached_item(cache_key: str, record_index: int):

    result = []

    # Redis first
    r = get_redis()
    if r:
        try:
            cached = r.get(cache_key)
            if cached:
                result = tuple(json.loads(cached))
        except RedisError:
            pass

    # Memory fallback
    if cache_key in _memory_cache:
        result = _memory_cache[cache_key]

    if record_index not in result:
        result.append(record_index)

    # Cacheia
    serialized = json.dumps(result)
    if r:
        try:
            r.set(cache_key, serialized, ex=TTL_SECONDS)
        except RedisError:
            pass
    _memory_cache[cache_key] = result

    return result
