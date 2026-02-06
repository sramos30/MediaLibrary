# conexão básica + query simples
#!/usr/bin/env python3
"""Testa conexão básica com MySQL."""

import sys
import mysql.connector

try:
    conn = mysql.connector.connect(
        host='mysql',
        user='dedup_user',          # ajuste se mudou
        password='sua-senha-aqui',  # ajuste
        database='dedup_db'
    )
    print("Conexão MySQL OK!")
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()[0]
    print(f"Versão do MySQL: {version}")
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f"Erro no MySQL: {e}")
    sys.exit(1)