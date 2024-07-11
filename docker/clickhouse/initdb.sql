use jager;

DROP TABLE IF EXISTS carriers;
CREATE TABLE IF NOT EXISTS carriers (id UInt32 NOT NULL, name VARCHAR NOT NULL, gsk VARCHAR NOT NULL, PRIMARY KEY id) ENGINE = MergeTree();

DROP TABLE IF EXISTS ct_records;
CREATE TABLE IF NOT EXISTS ct_records (label VARCHAR NOT NULL, sigma VARCHAR NOT NULL, ct VARCHAR NOT NULL, PRIMARY KEY (label, sigma)) ENGINE = MergeTree();
ALTER TABLE ct_records ADD INDEX label_index label TYPE minmax GRANULARITY 4;

DROP TABLE IF EXISTS raw_cdrs;
CREATE TABLE IF NOT EXISTS raw_cdrs (id VARCHAR NOT NULL, status TinyInt DEFAULT 0, src VARCHAR NOT NULL, dst VARCHAR NOT NULL, ts VARCHAR NOT NULL, prev VARCHAR NOT NULL, curr VARCHAR NOT NULL, next VARCHAR NOT NULL, PRIMARY KEY id) ENGINE = MergeTree();

DROP TABLE IF EXISTS subscribers;
CREATE TABLE IF NOT EXISTS subscribers (id UInt32 NOT NULL, phone VARCHAR NOT NULL, carrier UInt32 NOT NULL, PRIMARY KEY id) ENGINE = MergeTree();

DROP TABLE IF EXISTS edges;
CREATE TABLE IF NOT EXISTS edges (id VARCHAR NOT NULL, src UInt32 NOT NULL, dst UInt32 NOT NULL, PRIMARY KEY id) ENGINE = MergeTree();