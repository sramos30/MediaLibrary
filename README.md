# MediaLibrary
A project to organize all media files distributed in all kind of archive

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
'''
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
'''

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
5. Crie → copie a URL (https ou SSH): 

### 3. Estrutura local inicial

```bash
mkdir dedup-arquivos-antigos
cd dedup-arquivos-antigos

git init
git remote add origin https://github.com/SEU-USUARIO/dedup-arquivos-antigos.git
