from pathlib import Path
from scripts.utils.cache_utils import get_cached_prefix

TEST_DIR = Path("/scan-data/lego/42083-BUGATTI CHIRON-LEGO TECHNIC/images/")  # ou uma pasta montada

files = [p for p in TEST_DIR.rglob("*") if p.is_file()][:100]  # limite para não demorar

print(f"Escaneando {len(files)} arquivos em {TEST_DIR}")

for file in files:
    size, prefix_hash, read_size = get_cached_prefix(file)
    print(f"{file.relative_to(TEST_DIR)}: size={size}, hash={prefix_hash:016x}")
