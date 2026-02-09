#!/usr/bin/env python3
"""Calcula hash completo incremental em blocos de 64KiB, usando prefix como IV."""

import sys
from pathlib import Path
import sqlalchemy as sa
import xxhash
from tqdm import tqdm

BLOCK_SIZE = 64 * 1024  # 64 KiB

# Configurações
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

        if len(files) < 2:
            print("  Grupo tem menos de 2 arquivos — pulando.")
            continue

        # Escolhe master (primeiro alfabeticamente)
        master_id, master_path_str = files[0]
        master_path = Path(master_path_str)
        print(f"  Master: {master_path.name} ({master_path})")

        # Hash completo do master (começa com prefix como IV)
        master_h = xxhash.xxh3_128()
        master_h.update(prefix_hash.to_bytes(8, 'big'))  # usa prefix como IV inicial
        master_blocks = 1  # conta o prefix como bloco 1

        # Lê a partir do bloco 2 (pula os primeiros 64 KiB)
        try:
            with open(master_path, "rb") as f:
                f.seek(BLOCK_SIZE)  # pula o prefixo já hashado
                total_size_remaining = size - BLOCK_SIZE
                with tqdm(total=total_size_remaining, unit='B', unit_scale=True, desc="Hash master") as pbar:
                    while chunk := f.read(BLOCK_SIZE):
                        master_h.update(chunk)
                        master_blocks += 1
                        pbar.update(len(chunk))
            master_full_hash = master_h.hexdigest()
            conn.execute(sa.text("""
                UPDATE file_metadata 
                SET full_hash = :full_hash, partial_blocks = :blocks
                WHERE id = :id
            """), {"full_hash": master_full_hash, "blocks": master_blocks, "id": master_id})
            print(f"  Master hash completo: {master_full_hash} (blocks: {master_blocks})")
        except Exception as e:
            print(f"  Erro ao ler master {master_path}: {e}")
            continue

        # Para cada outro arquivo, compara bloco a bloco com master
        for id, path_str in files[1:]:
            path = Path(path_str)
            print(f"  Comparando com {path.name} ({path})...")
            h = xxhash.xxh3_128()
            h.update(prefix_hash.to_bytes(8, 'big'))  # mesmo IV
            blocks_equal = 1  # prefix já igual
            full_hash = None
            try:
                with open(path, "rb") as f:
                    f.seek(BLOCK_SIZE)  # pula prefixo
                    total_remaining = size - BLOCK_SIZE
                    with tqdm(total=total_remaining, unit='B', unit_scale=True, desc="Comparando") as pbar:
                        while chunk := f.read(BLOCK_SIZE):
                            # Aqui você pode comparar com master se quiser parar cedo
                            # (mas para hash completo, continua calculando)
                            h.update(chunk)
                            blocks_equal += 1
                            pbar.update(len(chunk))
                        full_hash = h.hexdigest()
                conn.execute(sa.text("""
                    UPDATE file_metadata 
                    SET full_hash = :full_hash, partial_blocks = :blocks
                    WHERE id = :id
                """), {"full_hash": full_hash, "blocks": blocks_equal, "id": id})
                print(f"  Hash completo: {full_hash} (blocks: {blocks_equal})")
            except Exception as e:
                print(f"  Erro ao ler {path}: {e}")

    conn.commit()

print("\nVerificação concluída!")
