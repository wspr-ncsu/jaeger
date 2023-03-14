-- Dropping routing_records_provider_id_fk constraint on cdrs Table if exist:
ALTER TABLE IF EXISTS cdrs DROP CONSTRAINT routing_records_provider_id_fk;

-- Dropping Providers table if exist:
DROP TABLE IF EXISTS Providers;

-- Recreating Providers table if does not exists:
CREATE TABLE IF NOT EXISTS Providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

-- Dropping cdrs table if exist:
DROP TABLE IF EXISTS cdrs;

-- Recreating cdrs table if does not exist:
CREATE TABLE IF NOT EXISTS cdrs (
    cci VARCHAR NOT NULL,
    tbc VARCHAR NOT NULL,
    tfc VARCHAR NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cci, tbc, tfc)
);

