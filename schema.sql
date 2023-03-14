-- Dropping routing_records_provider_id_fk constraint on TraceRecords Table if exist:
ALTER TABLE IF EXISTS TraceRecords DROP CONSTRAINT routing_records_provider_id_fk;

-- Dropping Providers table if exist:
DROP TABLE IF EXISTS Providers;

-- Recreating Providers table if does not exists:
CREATE TABLE IF NOT EXISTS Providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

-- Dropping tracerecords table if exist:
DROP TABLE IF EXISTS TraceRecords;

-- Recreating Tracerecords table if does not exist:
CREATE TABLE IF NOT EXISTS TraceRecords (
    traceback VARCHAR NOT NULL,
    traceforward VARCHAR NOT NULL,
    provider_id INTEGER NULL DEFAULT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (traceback, traceforward),
    CONSTRAINT routing_records_provider_id_fk FOREIGN KEY (provider_id) REFERENCES Providers(id)
);

