CREATE DATABASE IF NOT EXISTS dedup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE dedup_db;

CREATE TABLE IF NOT EXISTS file_metadata (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_path VARCHAR(2048) NOT NULL,
    file_name VARCHAR(512) NOT NULL,
    parent_dir VARCHAR(2048),
    size_bytes BIGINT NOT NULL,
    prefix_xxh3_64 BIGINT UNSIGNED NOT NULL DEFAULT 0,
    prefix_size INT UNSIGNED NOT NULL DEFAULT 0,
    sha256_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL,
    creation_timestamp DATETIME,
    scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_full_path (full_path(768)),
    INDEX idx_size_prefix (size_bytes, prefix_xxh3_64),
    INDEX idx_sha256 (sha256_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
