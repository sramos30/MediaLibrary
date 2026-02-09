# comparação entre discos
#!/usr/bin/env python3
"""Compara candidatos entre discos diferentes com hash parcial."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))  # ajuste de path

from pathlib import Path
import sqlalchemy as sa
import xxhash
from tqdm import tqdm

BLOCK_SIZE = 64 * 1024

MYSQL_URL = "mysql+mysqlconnector://dedup_user:urP%40ssw0rd%21@mysql/dedup_db?charset=utf8mb4"
engine = sa.create_engine(MYSQL_URL)

DISK1 = "HD-Antigo"  # ajuste
DISK2 = "MediaAtual"  # ajuste

with engine.connect() as conn:
    # Busca candidatos entre discos diferentes
    candidates = conn.execute(sa.text("""
        SELECT f1.id AS id1, f1.full_path AS path1, f1.partial_blocks AS blocks1,
               f2.id AS id2, f2.full_path AS path2, f2.partial_blocks AS blocks2,
               f1.size_bytes, f1.prefix_xxh3_64
        FROM file_metadata f1
        JOIN file_metadata f2 ON f1.size_bytes = f2.size_bytes AND f1.prefix_xxh3_64 = f2.prefix_xxh3_64
        WHERE f1.source_disk = :disk1 AND f2.source_disk = :disk2
          AND f1.id != f2.id
        ORDER BY f1.size_bytes DESC
    """), {"disk1": DISK1, "disk2": DISK2}).fetchall()

    if not candidates:
        print("Nenhum candidato entre discos.")
        sys.exit(0)

    print(f"Encontrados {len(candidates)} candidatos entre {DISK1} e {DISK2}")

    for id1, path1_str, blocks1, id2, path2_str, blocks2, size, prefix_hash in candidates:
        path1 = Path(path1_str)
        path2 = Path(path2_str)
        print(f"\nComparando {path1.name} ({DISK1}) vs {path2.name} ({DISK2})")

        # Escolhe o líder com menos blocos salvos
        if blocks1 is None or blocks2 is None or blocks1 <= blocks2:
            leader_path, follower_path, leader_blocks = path1, path2, blocks1
        else:
            leader_path, follower_path, leader_blocks = path2, path1, blocks2

        if leader_blocks is None:
            leader_blocks = (size + BLOCK_SIZE - 1) // BLOCK_SIZE

        leader_h = xxhash.xxh3_128()
        leader_h.update(prefix_hash.to_bytes(8, 'big'))
        follower_h = xxhash.xxh3_128()
        follower_h.update(prefix_hash.to_bytes(8, 'big'))

        blocks_equal = 1
        differ_at = None

        try:
            with open(leader_path, "rb") as lf, open(follower_path, "rb") as ff:
                lf.seek(BLOCK_SIZE)
                ff.seek(BLOCK_SIZE)
                total_remaining = size - BLOCK_SIZE
                with tqdm(total=total_remaining, unit='B', unit_scale=True, desc="Comparando blocos") as pbar:
                    block_num = 1
                    while chunk_l := lf.read(BLOCK_SIZE):
                        chunk_f = ff.read(BLOCK_SIZE)
                        if chunk_l != chunk_f:
                            differ_at = block_num + 1
                            print(f"    Diferem no bloco {differ_at} — parando.")
                            break
                        leader_h.update(chunk_l)
                        follower_h.update(chunk_f)
                        blocks_equal += 1
                        block_num += 1
                        pbar.update(len(chunk_l))
                    else:
                        print("    Iguais até o fim do líder.")
            # Salva resultados
            conn.execute(sa.text("""
                UPDATE file_metadata SET partial_blocks = :blocks WHERE id IN (:id1, :id2)
            """), {"blocks": blocks_equal, "id1": id1, "id2": id2})

            if differ_at is None:
                print("    Candidato para nova passagem (precisa hash completo).")
                conn.execute(sa.text("""
                    UPDATE file_metadata SET needs_full_hash = TRUE WHERE id IN (:id1, :id2)
                """), {"id1": id1, "id2": id2})
            else:
                conn.execute(sa.text("""
                    UPDATE file_metadata SET needs_full_hash = FALSE WHERE id IN (:id1, :id2)
                """), {"id1": id1, "id2": id2})
        except Exception as e:
            print(f"  Erro ao comparar: {e}")

    conn.commit()

print("Comparação concluída!")