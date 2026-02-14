# MediaLibrary
A project to organize all media files distributed in all kind of archive
git clone --single-branch --branch master git@github.com:sramos30/MediaLibrary.git .
git clone --single-branch --branch without_python_vs git@github.com:sramos30/MediaLibrary.git .

git branch --show-current
git push --set-upstream origin <branch>

# criar o ambiente virtual para o python e para o Jupyter

python -m venv .venv
Ativar o ambiente
Windows: .venv\Scripts\activate
Linux/Mac: source .venv/bin/activate

para fechar o .env:
deactivate

instalar todos os pacotes no ambiente virtual
pip install -r requirements.txt

# destruir o container
docker compose down -v


# Projeto Deduplicação e Organização de Arquivos Antigos

**Objetivo principal**  
Organizar e deduplicar arquivos de múltiplos HDs externos antigos (fotos, vídeos, desenhos animados, Cirque du Soleil, filmes infantis leves, documentos, etc.), criando um arquivo único de conteúdo único em um disco final, preservando estrutura por origem e evitando perda de dados.

**Contexto emocional**  
O projeto nasceu da necessidade de manter uma "média" organizada e variada de conteúdos leves e infantis para distrair e alegrar minha esposa durante o dia (desenhos animados, trechos de espetáculos, filmes leves), já que ela passa a todo o tempo na cama devido à condição de saúde (Demência Fronto Temporal e Tetraplegia).

**Tecnologias principais**  
- Docker Desktop (Windows 11)  
- MySQL 8  
- phpMyAdmin  
- Python 3.11+ (com Jupyter para experimentação)  
- Redis (cache de prefix hashes)  
- xxHash (xxh3_64 ou xxh3_128) para detecção rápida de candidatos  
- SHA-256 (ou xxh3 full) para confirmação de duplicatas reais  
- tqdm (progress bars)  
- sqlalchemy + mysql-connector-python

## Estrutura Recomendada do Repositório

dedup-arquivos-antigos/
├── docker-compose.yml
├── Dockerfile.python
├── requirements.txt
├── init-sql/
│   └── 01-init-tables.sql
├── scripts/
│   ├── scan_files_fast.py               # scan inicial + prefix hash + cache Redis
│   ├── compute_full_hash_duplicates.py  # hash completo só em candidatos
│   ├── merge_to_final.py                # copia únicos para disco final
│   └── utils/
│       └── cache_utils.py               # lógica Redis + fallback
├── notebooks/                           # experimentos Jupyter
└── README.md


## Passo a Passo Completo de Implantação (Windows 11 + Docker Desktop)

### 1. Pré-requisitos

- Instale **Docker Desktop** (com WSL 2 backend ativado)
- Git instalado
- Um editor bom (VS Code + extensão Dev Containers recomendada)
- HDs externos montados como letras (ex: E:, F:, G:) → mapeie no Docker

### 2. Crie o repositório no GitHub

1. Vá para github.com → New repository
2. Nome: MediaLibrary 
3. Repositório Público
4. README criado e editado antes da estrutura ser criada localmente
5. URL (SSH): git clone git@github.com:sramos30/MediaLibrary.git 

### 3. Estrutura local inicial

```bash
mkdir MediaLibrary
cd MediaLibrary

git init
git remote add origin https://github.com/SEU-USUARIO/dedup-arquivos-antigos.git

# create a cifs share
mkdir -p ./MediaDisk && mount -t cifs //192.168.69.9/MediaDisk ./MediaDisk -o credentials=/app/credentials.sramos30,vers=3.0,file_mode=0777,dir_mode=0777

credentials.sramos30
====================
username=sramos30
password=mcLiamada1


# docker compose
docker compose down -v --remove-orphans --rmi all

# open python dev container
docker exec -it medialibrary-python-1 /bin/bash

# docker compose CIFS Volume samples
  - MediaDiskSmb:/mediadisk:ro
  - BigDiskSmb:/bigdisk:ro
  - DataDiskSmb:/datadisk:ro
  
  MediaDiskSmb:
    driver: local
    driver_opts:
      type: cifs
      device: "${MEDIADISK_SERVER}"
      o: "username=${MEDIADISK_USER},password=${MEDIADISK_PASSWORD},uid=0,gid=0,vers=3.0,iocharset=utf8,dir_mode=0777,file_mode=0777"
  BigDiskSmb:
    driver: local
    driver_opts:
      type: cifs
      device: "${BIGDISK_SERVER}"
      o: "username=${BIGDISK_USER},password=${BIGDISK_PASSWORD},uid=0,gid=0,vers=3.0,iocharset=utf8,dir_mode=0777,file_mode=0777"
  DataDiskSmb:
    driver: local
    driver_opts:
      type: cifs
      device: "${DATADISK_SERVER}"
      o: "username=${DATADISK_USER},password=${DATADISK_PASSWORD},uid=0,gid=0,vers=3.0,iocharset=utf8,dir_mode=0777,file_mode=0777"

