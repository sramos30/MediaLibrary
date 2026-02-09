
# calcula o hash do prefixo de um arquivo
#!/usr/bin/env python3
import os
import json
import redis
from redis.exceptions import RedisError
from pathlib import Path
import xxhash

# Configs
PREFIX_SIZE = 64 * 1024
HASH_FUNC = xxhash.xxh3_64

HASH_BLK_SIZE = 64 * 1024  # 64KB
HASH_NUM_BLKS = [1, 16, 256, 4096, 65536]
HASH_OFFSETS = [0, HASH_BLK_SIZE, HASH_BLK_SIZE * HASH_NUM_BLKS[2], HASH_BLK_SIZE * HASH_NUM_BLKS[3], HASH_BLK_SIZE * HASH_NUM_BLKS[4]]

def get_hash_block(blkNum:int, iv:int, filePath:Path):
  if blkNum >= len(HASH_OFFSETS) or blkNum < 1:
    return f"blkNum {blkNum} out of range"

  try:
      offset = HASH_OFFSETS[blkNum-1]
      qtd_blks = HASH_NUM_BLKS[blkNum-1]
      file_size = os.path.getsize(filePath)


      read_size = min(PREFIX_SIZE, os.path.getsize(filePath))

      with open(filePath, "rb") as f:
          data = f.read(read_size)
          h = HASH_FUNC()
          h.update(data)
          return hex(h.intdigest())
  except OSError as err:
    print( f"exception ({err}) in get_hash_block: {filePath}")      

  return None
# retorna as informacoes de um arquivo

def getFileInfo(filePath:Path):
    entry = {}
    entry['name'] = ''
    entry['path'] = ''
    entry['hash1'] = 0
    entry['hash2'] = 0
    entry['hash3'] = 0
    entry['hash4'] = 0
    entry['hash5'] = 0
    entry['ST_INO'] = 0
    entry['ST_DEV'] = 0
    entry['ST_NLINK'] = 0
    entry['ST_SIZE'] = 0
    entry['ST_MTIME'] = 0

    try:
        fullPath = os.path.abspath(filePath)
        entry['name'] = os.path.basename(fullPath)  
        entry['path'] = fullPath.replace(entry['name'],'')
        fileStat = os.stat(fullPath)
        entry['ST_INO'] = fileStat[stat.ST_INO]
        entry['ST_DEV'] = fileStat[stat.ST_DEV]
        entry['ST_NLINK'] = fileStat[stat.ST_NLINK]
        entry['ST_SIZE'] = fileStat[stat.ST_SIZE]
        entry['ST_MTIME'] = fileStat[stat.ST_MTIME]

        read_size = min(entry['ST_SIZE'], PREFIX_SIZE)
        with open(filePath, "rb") as f:
            data = f.read(read_size)
            h = HASH_FUNC()
            h.update(data)
            entry['prefix_hash'] = hex(h.intdigest())      

        return entry
    except OSError as err:
        print( f"exception ({err}) in getFileInfo: {filePath}")      

    return None
