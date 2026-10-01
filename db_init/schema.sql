CREATE TABLE scans (
    id SERIAL PRIMARY KEY,
    project_name TEXT,
    target_license TEXT,
    scanned_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE dependencies (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id),
    name TEXT,
    version TEXT,
    license TEXT,
    risk TEXT
);
