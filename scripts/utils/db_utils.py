# base do banco de dados
#!/usr/bin/env python3

import sqlalchemy as sa
from sqlalchemy import String, Double, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import sessionmaker, Session

class Base(DeclarativeBase):
    pass

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    __table_args__ = (
        Index("idx_path_id", "path_id"),
        Index("idx_size_prefix", "st_dev", "st_ino"),
        Index("idx_hash1", "st_size", "hash1"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    full_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    path_id: Mapped[str | None] = mapped_column(String(32), default=None)
    hash1: Mapped[str | None] = mapped_column(String(32), default=None)
    hash2: Mapped[str | None] = mapped_column(String(32), default=None)
    hash3: Mapped[str | None] = mapped_column(String(32), default=None)
    hash4: Mapped[str | None] = mapped_column(String(32), default=None)
    hash5: Mapped[str | None] = mapped_column(String(32), default=None)

    st_dev: Mapped[str | None] = mapped_column(String(32), default=None)
    st_ino: Mapped[str | None] = mapped_column(String(32), default=None)
    st_size: Mapped[int] = mapped_column(BIGINT(unsigned=True), default=0)
    st_mtime: Mapped[float] = mapped_column(Double, default=0.0)

# from redis.exceptions import RedisError

MYSQL_URL = "mysql+mysqlconnector://dedup_user:urP%40ssw0rd%21@localhost/dedup_db?charset=utf8mb4"

# Conexão Redis lazy com fallback
# _redis_client = None

# Create ONE engine for the whole application/script
engine = sa.create_engine(
    MYSQL_URL,
    pool_size=10,          # adjust based on your needs / server capacity
    max_overflow=15,       # allows temporary bursts
    pool_timeout=30,       # seconds to wait for a connection from pool
    pool_recycle=1800,     # recycle connections after ~30 min (helps with stale ones)
    pool_pre_ping=True     # very useful with MySQL — checks if connection is alive
)

# Create a session factory (recommended pattern)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False   # useful if you keep using objects after commit
)

# Cache local fallback
# _memory_cache = {}

# def get_redis():
#     global _redis_client
#     if _redis_client is None:
#         try:
#             _redis_client = redis.Redis(
#                 host=os.getenv('REDIS_HOST', 'localhost'),
#                 port=int(os.getenv('REDIS_PORT', 6379)),
#                 db=0,
#                 decode_responses=True,
#                 socket_timeout=2,
#                 socket_connect_timeout=2,
#                 retry_on_timeout=True
#             )
#             _redis_client.ping()  # teste
#         except RedisError as e:
#             print(f"Redis indisponível ({e}) → fallback para memória")
#             _redis_client = None
#     return _redis_client

def insert_entry( data_entry: FileMetadata ):
    result = {}
    result['row_count'] = 0

    try:
        with SessionLocal() as session:
            session.add(data_entry)
            session.commit()
        result['row_count'] = 1
    except Exception as e:
        result['error'] = f"Erro no MySQL: {e}"

    return result

def get_entry_by_id(file_id: int) -> FileMetadata | None:
    with SessionLocal() as session:
        return session.get(FileMetadata, file_id)

def get_entry_by_path_id(path_id: str) -> FileMetadata | None:
    with SessionLocal() as session:  
        stmt = sa.select(FileMetadata).where(
            FileMetadata.path_id == path_id
        )
        return session.scalar(stmt)

def get_by_inode(st_dev: str, st_ino: str) -> FileMetadata | None:
    with SessionLocal() as session:  
        stmt = sa.select(FileMetadata).where(
            FileMetadata.st_dev == st_dev,
            FileMetadata.st_ino == st_ino
        )
        return session.scalar(stmt)

def update_file_basic(file_id: int, new_values: dict):
    with SessionLocal() as session:
        # Load the existing record (or None if missing)
        file_obj = session.get(FileMetadata, file_id)

        if file_obj is None:
            print(f"No file found with id={file_id}")
            return None

        # Update only the fields you want to change
        for key, value in new_values.items():
            if hasattr(file_obj, key):
                setattr(file_obj, key, value)
            else:
                print(f"Warning: {key} not a valid attribute")

        # Optional: if you want to be explicit about which fields changed
        # file_obj.name = new_values.get('name', file_obj.name)
        # file_obj.full_path = new_values.get('full_path', file_obj.full_path)
        # ... etc.

        session.commit()          # emits UPDATE WHERE id = ?
        # session.refresh(file_obj) # optional: reload from DB if server defaults/triggers exist

        return file_obj


# def get_db_entry(cache_key: str):

#     result = []

#     # Redis first
#     r = get_redis()
#     if r:
#         try:
#             cached = r.get(cache_key)
#             if cached:
#                 result = tuple(json.loads(cached))
#         except RedisError:
#             pass
#     else:
#         # Memory fallback
#         if cache_key in _memory_cache:
#             result = _memory_cache[cache_key]

#     return result

# def set_db_entry(cache_key: str, entry: dict):

#     result = {}

#     # Redis first
#     r = get_redis()
#     if r:
#         try:
#             cached = r.get(cache_key)
#             if cached:
#                 result = json.loads(cached)        except RedisError:
#             pass

#     # Memory fallback
#     if cache_key in _memory_cache:
#         result = _memory_cache[cache_key]

#     if record_index not in result:
#         result.append(record_index)

#     # Cacheia
#     serialized = json.dumps(result)
#     if r:
#         try:
#             r.set(cache_key, serialized, ex=TTL_SECONDS)
#         except RedisError:
#             pass
#     _memory_cache[cache_key] = result

#     return result

