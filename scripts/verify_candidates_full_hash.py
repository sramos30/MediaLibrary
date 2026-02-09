# verificação de hash completo em candidatos
#!/usr/bin/env python3
"""Calcula hash completo em grupos de candidatos (cnt >= 2)."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))  # ajuste de path

from pathlib import Path
import sqlalchemy as sa
import xxhash

MYSQL_URL = "mysql+mysqlconnector://dedup_user:urP%40ssw0rd%21@mysql/dedup_db?charset=utf8mb4"
engine = sa.create_engine(MYSQL_URL)

with engine.connect() as conn:
    # Busca grupos candidatos
    groups = conn.execute(sa.text("""
        SELECT size_bytes, prefix_xxh3_64, COUNT(*) AS cnt
        FROM file_metadata
        GROUP BY size_bytes, prefix_xxh3_64
        HAVING cnt >= 2
        ORDER BY cnt DESC
    """)).fetchall()

    if not groups:
        print("Nenhum grupo candidato encontrado (cnt >= 2).")
        sys.exit(0)

    print(f"Encontrados {len(groups)} grupos candidatos")

    for size, prefix_hash, cnt in groups:
        print(f"\nGrupo: size={size:,} bytes, prefix_hash={prefix_hash:016x}, cnt={cnt}")

        # Busca arquivos desse grupo
        files = conn.execute(sa.text("""
            SELECT id, full_path
            FROM file_metadata
            WHERE size_bytes = :size AND prefix_xxh3_64 = :prefix
            ORDER BY full_path
        """), {"size": size, "prefix": prefix_hash}).fetchall()

        hashes = {}
        for id, path_str in files:
            path = Path(path_str)
            if not path.exists():
                print(f"  Arquivo não encontrado: {path}")
                continue

            print(f"  Calculando hash completo para {path.name} ({path})...")
            h = xxhash.xxh3_128()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            full_hash = h.hexdigest()
            hashes[full_hash] = hashes.get(full_hash, []) + [path_str]

            conn.execute(sa.text("""
                UPDATE file_metadata 
                SET full_hash = :full_hash
                WHERE id = :id
            """), {"full_hash": full_hash, "id": id})

        # Resultado do grupo
        if len(hashes) == 1:
            print("  Resultado: DUPLICATAS REAIS (todos hashes completos iguais)")
        else:
            print("  Resultado: NÃO são duplicatas reais (hashes completos diferentes)")

        for full_hash, paths in hashes.items():
            print(f"    Hash completo: {full_hash}")
            print(f"      Caminhos: {', '.join(paths)}")

    conn.commit()

print("Verificação concluída!")