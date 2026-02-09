#!/usr/bin/env python3
"""Exporta tabela file_metadata para CSV usando pandas."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))  # resolve import de scripts

from scripts.setup_path import *  # importa e ajusta o path

from pathlib import Path
import sqlalchemy as sa
from scripts.utils.cache_utils import get_cached_prefix

import pandas as pd

# Conexão (ajuste senha se necessário)
engine = sa.create_engine("mysql+mysqlconnector://dedup_user:urP%40ssw0rd%21@mysql/dedup_db?charset=utf8mb4")

# Export CSV automático
df = pd.read_sql("SELECT * FROM file_metadata", engine)
df.to_csv("/app/export_file_metadata_atualizado.csv", index=False)
print("CSV atualizado automaticamente em /app/export_file_metadata_atualizado.csv")

