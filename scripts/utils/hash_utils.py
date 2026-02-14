# calcula o hash do prefixo de um arquivo
#!/usr/bin/env python3
import os
from pathlib import Path
import xxhash

# Configs
HASH_FUNC = xxhash.xxh3_64
HASH_BLK_SIZE = 64 * 1024  # 64KB
HASH_NUM_BLKS = [1, 16, 16**2, 16**3, 16**4]  # Exemplo: 1, 16, 256, 4096, 65536, 1048576
HASH_OFFSETS = [
    [0, HASH_BLK_SIZE-1], 
    [HASH_BLK_SIZE, HASH_BLK_SIZE * 16 - 1], 
    [HASH_BLK_SIZE * 16, HASH_BLK_SIZE * 16**2 - 1], 
    [HASH_BLK_SIZE * 16**2, HASH_BLK_SIZE * 16**3-1], 
    [HASH_BLK_SIZE * 16**3, HASH_BLK_SIZE * 16**4-1],
  ]

def get_hash_string(s:str):
    retdict = []
    retdict['rc'] = 0
    retdict['hash_digest'] = ''

    try:
      h = HASH_FUNC()
      h.update(s)
      retdict['hash_digest'] = h.hexdigest()
      retdict['rc'] = 1
    except OSError as err:
      retdict['rc'] = -1
      retdict["msg"] = f"exception ({err}) in get_hash_string: {s}"

    return retdict

def get_hash_block(blkNum:int, iv:str, filePath:Path):
  rc = {}
  rc["rc"] = 0

  if not os.path.exists(filePath):
    rc["msg"] = f"file: {filePath} não existe!"
    return rc

  rc["filesize"] = os.path.getsize(filePath)

  if blkNum >= len(HASH_OFFSETS) or blkNum < 0:
    rc["msg"] = f"Bloco: {blkNum} está fora do intervalo permitido (0-{len(HASH_OFFSETS)-1})!"
    return rc

  if HASH_OFFSETS[blkNum][0] >= rc["filesize"]:
    rc["msg"] = f"Bloco: {blkNum} tem offset inicial ({HASH_OFFSETS[blkNum][0]}) maior que o tamanho do arquivo ({rc["filesize"]})!"
    return rc

  of = HASH_OFFSETS[blkNum][1]
  last_blk_size = 0
  qtd_blks = HASH_NUM_BLKS[blkNum]

  if blkNum == len(HASH_OFFSETS)-1:
    of = rc["filesize"]-1
    qtd_blks = (of - HASH_OFFSETS[blkNum][0] + 1) // HASH_BLK_SIZE
    last_blk_size = (of - HASH_OFFSETS[blkNum][0] + 1) % HASH_BLK_SIZE
  elif of >= rc["filesize"]:
    of = rc["filesize"] - 1
    qtd_blks = HASH_NUM_BLKS[blkNum]

    if HASH_OFFSETS[blkNum][1] > of:
      qtd_blks = (of - HASH_OFFSETS[blkNum][0] + 1) // HASH_BLK_SIZE
      last_blk_size = (of - HASH_OFFSETS[blkNum][0] + 1) % HASH_BLK_SIZE

  rc["oi"] = "offset initial:", HASH_OFFSETS[blkNum][0]
  rc["of"] = "offset final", of
  rc["qy"] = "qtd_bytes", of-HASH_OFFSETS[blkNum][0]+1
  rc["qb"] = "qtd_blks:", qtd_blks
  rc["lbs"] = "last_blk_size:", last_blk_size
  rc["iv"] = iv
  rc["digest"] = ""

  try:
      h = HASH_FUNC()
      h.update(iv)

      with open(filePath, "rb") as f:
        for blk in range(qtd_blks):
          data = f.read(HASH_BLK_SIZE)
          h.update(data)
        if last_blk_size > 0:
            data = f.read(last_blk_size)
            h.update(data)
      rc["digest"] = h.hexdigest()
      rc["rc"] = 1
  except OSError as err:
    rc["msg"] = f"exception ({err}) in get_hash_block: {filePath}"

  return rc

