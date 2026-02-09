# teste de conexão MySQL
#!/usr/bin/env python3
"""Testa conexão básica com MySQL."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))  # ajuste de path

import sqlalchemy as sa

MYSQL_URL = "mysql+mysqlconnector://dedup_user:urP%40ssw0rd%21@mysql/dedup_db?charset=utf8mb4"

try:
    engine = sa.create_engine(MYSQL_URL)
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT VERSION()"))
        version = result.fetchone()[0]
        print("Conexão MySQL OK!")
        print(f"Versão do MySQL: {version}")
    sys.exit(0)
except Exception as e:
    print(f"Erro no MySQL: {e}")
    sys.exit(1)