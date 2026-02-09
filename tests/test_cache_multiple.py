# teste com múltiplos arquivos
#!/usr/bin/env python3
"""Testa cache em múltiplos arquivos."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))  # ajuste de path

from pathlib import Path
from scripts.utils.cache_utils import get_cached_prefix


FILES = [
    Path("/app/requirements.txt"),
    Path("/app/Dockerfile.python"),
    Path("/app/.gitignore")  # ou outro arquivo pequeno que exista
]

for file in FILES:
    if file.exists():
        print(f"\nTestando {file.name}")
        size1, hash1, read1 = get_cached_prefix(file)
        print(f"  Primeira: size={size1}, hash={hash1:016x}")

        size2, hash2, read2 = get_cached_prefix(file)
        print(f"  Segunda: size={size2}, hash={hash2:016x}")
