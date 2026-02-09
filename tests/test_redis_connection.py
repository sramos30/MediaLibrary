# teste de Redis
#!/usr/bin/env python3
"""Testa conexão básica com Redis."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))  # ajuste de path

import redis

try:
    r = redis.Redis(host='redis', port=6379, decode_responses=True)
    pong = r.ping()
    print(f"Redis ping: {pong}")  # Deve ser True

    # Teste de escrita/leitura
    r.set('test_key', 'Olá do teste!')
    value = r.get('test_key')
    print(f"Valor lido: {value}")

    print("Redis OK!")
    sys.exit(0)
except Exception as e:
    print(f"Erro no Redis: {e}")
    sys.exit(1)