# opcional: shell script para rodar todos de uma vez
#!/bin/bash
set -e

echo "=== Testando Redis ==="
python -m tests.test_redis_connection

echo -e "\n=== Testando Cache Prefix ==="
python -m tests.test_cache_prefix

echo -e "\n=== Testando MySQL ==="
python tests.test_mysql_connection

echo -e "\nTodos os testes passaram! 🎉"

