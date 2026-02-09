# teste de cache simples
#!/usr/bin/env python3
"""Testa o cache de prefix hash (hit vs miss)."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))  # ajuste de path

from pathlib import Path
from scripts.utils.cache_utils import get_cached_prefix

TEST_FILE = Path("/app/requirements.txt")  # ou outro arquivo pequeno

if not TEST_FILE.exists():
    print(f"Arquivo de teste não encontrado: {TEST_FILE}")
    sys.exit(1)

try:
    print("Primeira chamada (deve calcular):")
    size1, hash1, read1 = get_cached_prefix(TEST_FILE)
    print(f"  size={size1}, hash={hash1:016x}, read={read1}")

    print("\nSegunda chamada (deve vir do cache):")
    size2, hash2, read2 = get_cached_prefix(TEST_FILE)
    print(f"  size={size2}, hash={hash2:016x}, read={read2}")

    if hash1 == hash2:
        print("Cache funcionou! (hashes iguais)")
    else:
        print("Cache falhou! Hashes diferentes")

    sys.exit(0)
except Exception as e:
    print(f"Erro no cache: {e}")
    sys.exit(1)
    