# scan principal, com ROOT_DIR via sys.argv e source_disk com map amigável
#!/usr/bin/env python3
"""Scan pasta, usa cache Redis para prefix hash e grava/atualiza no MySQL."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))  # resolve import de scripts

from pathlib import Path
import sqlalchemy as sa
from scripts.utils.cache_utils import get_cached_prefix
from tqdm import tqdm
import pandas as pd

# Map amigável para nomes de disco (opcional - ajuste conforme seus mounts)
# Extrai o nome raiz do path (primeiro segmento após /)
def get_disk_name_from_path(path: Path) -> str:
    try:
        parts = path.parts
        if len(parts) >= 2 and parts[1]:
            root_name = parts[1]
            return root_name  # usa map se existir, senão nome bruto
        return "unknown"
    except Exception:
        return "unknown"

# Configurações MySQL
MYSQL_URL = "mysql+mysqlconnector://dedup_user:urP%40ssw0rd%21@mysql/dedup_db?charset=utf8mb4"
CURRENT_SHARE = "/local_resources/"

# ROOT_DIR: padrão ou via linha de comando
if len(sys.argv) > 1:
    ROOT_DIR = Path(sys.argv[1])
    print(f"Usando pasta informada: {ROOT_DIR}")
else:
    ROOT_DIR = Path(CURRENT_SHARE)  # default
    print(f"Usando pasta padrão: {ROOT_DIR}")

if not ROOT_DIR.is_dir():
    print(f"Diretório não encontrado: {ROOT_DIR}")
    sys.exit(1)

engine = sa.create_engine(MYSQL_URL)

files = [p for p in ROOT_DIR.rglob("*") if p.is_file()]

print(f"Processando {len(files)} arquivos em {ROOT_DIR}")

inserted = 0
updated = 0

with engine.connect() as conn:
    for file in tqdm(files, desc="Escaneando e gravando", unit="arquivo", position=0, leave=True):
        try:
            size, prefix_hash, read_size = get_cached_prefix(file)
            full_path = str(file.absolute())
            file_name = file.name
            parent_dir = str(file.parent.absolute())
            source_disk = get_disk_name_from_path(file)

            result = conn.execute(sa.text("""
                INSERT INTO file_metadata
                (full_path, file_name, parent_dir, size_bytes, prefix_xxh3_64, prefix_size, scan_timestamp, source_disk)
                VALUES (:path, :name, :parent, :size, :hash, :read, CURRENT_TIMESTAMP, :disk)
                ON DUPLICATE KEY UPDATE
                    file_name = :name,
                    parent_dir = :parent,
                    size_bytes = :size,
                    prefix_xxh3_64 = :hash,
                    prefix_size = :read,
                    scan_timestamp = CURRENT_TIMESTAMP,
                    source_disk = :disk
            """), {
                "path": full_path,
                "name": file_name,
                "parent": parent_dir,
                "size": size,
                "hash": prefix_hash,
                "read": read_size,
                "disk": source_disk
            })

            if result.rowcount > 0:
                inserted += 1
            else:
                updated += 1

            # if (inserted + updated) % 10 == 0:
            #     print(f"Processados {inserted + updated} arquivos...")
            if (inserted + updated) % 1000 == 0:
                conn.commit()

        except Exception as e:
            print(f"Erro em {file}: {e}")

    conn.commit()

print(f"Concluído! Novos: {inserted} | Atualizados: {updated}")

# # Export CSV automático
# df = pd.read_sql("SELECT * FROM file_metadata", engine)
# df.to_csv("/app/export_file_metadata_atualizado.csv", index=False)
# print("CSV atualizado automaticamente em /app/export_file_metadata_atualizado.csv")