import os, sys, tqdm
import glob, itertools
from os import listdir
import xxhash
from pathlib import Path, PurePath
from os.path import isfile, join
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..')) 

import scripts.utils.hash_utils as hu
from scripts.utils.general_utils import time_function

import scripts.utils.db_utils as db
from scripts.utils.db_utils import insert_entry, FileMetadata, get_by_inode, get_entry_by_id, update_file_basic

# @time_function
def getFileInfo(filePath:Path):
    entry = FileMetadata()
    entry.name = ''
    entry.full_path = ''
    entry.path_id = 0
    entry.hash1 = f"{-1}"
    entry.hash2 = ""
    entry.hash3 = ""
    entry.hash4 = ""
    entry.hash5 = ""
    entry.st_dev = 0
    entry.st_ino = 0

    entry.st_size = 0
    entry.st_mtime = 0

    try:
        fullPath = os.path.abspath(filePath)

        entry.name = os.path.basename(fullPath)
        entry.full_path = fullPath.replace(entry.name,'')

        fileStat = os.stat(fullPath)

        p = PurePath(fullPath).parts
        p2 = p[0:len(p)]

        base_path = 0
        for t in range(len(p2)-1,0,-1):
            p = os.path.join(*p2[0:t])

            if fileStat.st_dev != Path(p).stat().st_dev:
                base_path = t
                break

        p = tuple(p2[base_path+1:])
        h = xxhash.xxh3_64()
        h.update(f"{hex(fileStat.st_dev)}-{str(tuple( p2[base_path+1:])).lower()}")
        entry.path_id = h.hexdigest()

        entry.st_dev =   hex(fileStat.st_dev)
        entry.st_ino =   hex(fileStat.st_ino)
        entry.st_size =  fileStat.st_size
        entry.st_mtime = fileStat.st_mtime

        # get hash 0
        rc = hu.get_hash_block(0, "", fullPath)

        if rc and rc["rc"] != 0:
            entry.hash1 = rc["digest"]
        # else:
        #     print( rc["msg"] )

        return entry
    except OSError as err:
        print( f"exception ({err}) in getFileInfo: {fullPath}")

    return None

# @time_function
def scan_folder(srcPath: Path, file_list: list, dir_list: list):
    # print(f"srcPath: {srcPath}")
    if os.path.isfile(srcPath):
        file_list.append(srcPath)
    else:
        for f in itertools.chain(glob.iglob(join(srcPath, '.**')), glob.iglob(join(srcPath, '**'))):
            # print(f"item: {f}")
            try:
                if os.path.isfile(f):
                    file_list.append(f)
                elif os.path.isdir(f):
                    dir_list.append(f)
            except Exception as e:
                print(f"Erro ao acessar {f}: {e}")

# @time_function
def scan_files_and_folders(initial_dir: str):

  dir_list = [initial_dir]

  for srcPath in dir_list:
      file_list = []

      scan_folder(srcPath, file_list, dir_list)

      # print(f"Diretório: {srcPath} | Total de arquivos: {len(file_list)} | Total de diretórios: {len(dir_list)}")

      if len(file_list) > 0:
        for file in tqdm(file_list, desc=f"{srcPath} ", unit=" files", position=0, leave=True):
            fInfo = getFileInfo(file)

            exists = get_entry_by_id(fInfo.id)
            link_exists = get_by_inode(fInfo.st_dev, fInfo.st_ino)

            org_update = None

            if link_exists is not None:
                org_update = link_exists

            if exists is not None:
                org_update = exists

            if org_update is not None:
                new_values = {}

                if org_update.st_mtime != fInfo.st_mtime:
                    new_values['st_mtime'] = fInfo.st_mtime

                # if new_values:
                #     updated = update_file_basic(fInfo.id, new_values)
                #     if updated:
                #         print(f"Updated {fInfo.full_path}{fInfo.name} with {new_values}")
                #     else:
                #         print(f"Failed to update {fInfo.full_path}{fInfo.name}")

            if exists is None:
                if link_exists is None:
                    result = insert_entry(fInfo)
                    # if result['row_count'] < 1:
                    #     print( result )
                # else:
                #     print(f"Arquivo ({fInfo.full_path}{fInfo.name}) já existe com mesmo inode: {link_exists.full_path}{link_exists.name}")

scan_files_and_folders("C:/Resources/Kindle")
